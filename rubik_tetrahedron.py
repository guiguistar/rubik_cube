#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from op_transformations import Operation
from polyedre import Polyedre
from pygame_gestion_clavier import Gestion_clavier
from rubik_constants import couleurs_rubik,sommets_tetraedre,aretes_tetraedre,faces_tetraedre,couleurs_aretes_tetraedre,sommets_octaedre,faces_octaedre,couleurs_faces_aretes_tetraedre,couleurs_faces_octaedre,couleurs_faces_coins_tetraedre,aretes_octaedre

# =============================================================================
class Rubik_tetrahedron:
    '''
    Classe Rubik_tetrahedron : ... 
    '''

    # =============================================================================
    def __init__(self,ratio):

        self.ratio = ratio
        self.operations_queue=[]
        self.rtype='tetrahedron'

        # Pour écarter un peu les différentes pièces, on les translate un peu plus
        self.coeff_translation = 1.1
       
        # Construction d'un tétraèdre de référence qui servira à tracer les axes de la pyramide
        self.tetraedre_reference = Polyedre(sommets_tetraedre, aretes_tetraedre,faces_tetraedre, couleurs_rubik)

        # Tétraèdres des centres des arêtes (translations du tétraèdre de référence par chacun des
        # vecteurs demi-somme de couples d'extrémités; envisager une boucle
        self.tetraedres = []
        for i, arete in enumerate(aretes_tetraedre):
            self.tetraedres.append(Polyedre(sommets_tetraedre, 
                                            aretes_tetraedre, 
                                            faces_tetraedre, 
                                            couleurs_faces_aretes_tetraedre[i],
                                            [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[arete[0]], sommets_tetraedre[arete[1]])]))

        for i,sommet in enumerate(sommets_tetraedre):
            # fmv pas le centre de gravité
            if i != 4 :
                self.tetraedres.append(Polyedre(sommets_tetraedre, 
                                                aretes_tetraedre, 
                                                faces_tetraedre, 
                                                couleurs_faces_coins_tetraedre[i],
                                                [2*s*self.coeff_translation for s in sommet]))

        # Constructions des 4 octaèdres (translations de l'octaèdre de référence par chacun des vecteurs sommet du tétraèdre de référence)
        self.octaedres = []
        for i, sommet in enumerate(sommets_tetraedre):
            # fmv pas le centre de gravité
            if i != 4 :
                self.octaedres.append ( Polyedre(sommets_octaedre, 
                                                 aretes_octaedre,   
                                                 faces_octaedre, 
                                                 couleurs_faces_octaedre[i],
                                                 sommet,
                                                 -np.arccos(np.sqrt(3.)/3.), 
                                                 [1.,0.,0.]) )
        # translation des octaèdres
        # fmv : c'est quoi le calcul ici ?
        for i, octa in enumerate(self.octaedres):
            octa.translation_polyedre([(self.coeff_translation-1.) * s for s in self.tetraedre_reference.sommets_initiaux[i]]) 

    # =============================================================================
    # Afficher le rubik revient à afficher chacun de ses polyedres 
    def afficher(self):
        for octaedre in self.octaedres:
            octaedre.afficher()
        for tetraedre in self.tetraedres:
            tetraedre.afficher()
        #self.tetraedre_reference.afficher_axes()

    # =============================================================================
    # Tourner le rubik revient à tourner chacun de ses polyedres
    # fmv : n'est pas/plus utilisé
    #def rotation_rubik(self, angle, vecteur):
    #    for octaedre in self.octaedres:
    #        octaedre.rotation_polyedre(angle, vecteur)
    #    for tetraedre in self.tetraedres:
    #        tetraedre.rotation_polyedre(angle, vecteur)
   
    # =============================================================================
    # op : Objet de la classe Operation :
    #   op.vecteur : vecteur rotation
    #   op.ligne   : up/down
    #   op.sens    : +1,-1 sens de la rotation 
    def transformer_rubik(self, op, u=1) :

        if op.vecteur[0] == 0. and op.vecteur[1] == (0.75*np.sqrt(2./3.)) :
            k=0
        if op.vecteur[0] == -0.5 and op.vecteur[1] == -0.25*np.sqrt(2./3) :
            k=1
        if op.vecteur[0] == 0.5 and op.vecteur[1] == -0.25*np.sqrt(2./3) :
            k=2
        if op.vecteur[0] == 0. and op.vecteur[1] == -0.25* np.sqrt(2./3.):
            k=3

        if op.ligne == "up" :
            for tetraedre in self.tetraedres:
                # Test sur le produit scalaire entre OG' et OG
                test_tetra=sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[k]))
                if test_tetra > np.sqrt(2./3.) : 
                    tetraedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)
            for octaedre in self.octaedres:
                # Test sur le produit scalaire entre OG' et OG
                test_octa=sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[k]))
                if test_octa > np.sqrt(2./3.) : 
                    octaedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)

        if op.ligne == "middle" :
            for tetraedre in self.tetraedres:
                # Test sur le produit scalaire entre OG' et OG
                test_tetra=sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[k]))
                if test_tetra < np.sqrt(2./3.) and test_tetra > 0. : 
                    tetraedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)
            for octaedre in self.octaedres:
                # Test sur le produit scalaire entre OG' et OG
                test_octa=sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[k]))
                if test_octa < np.sqrt(2./3.) and test_octa > 0. : 
                    octaedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)

        if op.ligne == "down" :
            for tetraedre in self.tetraedres:
                # Test sur le produit scalaire entre OG' et OG
                test_tetra=sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[k]))
                if test_tetra < 0. : 
                    tetraedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)
            for octaedre in self.octaedres:
                # Test sur le produit scalaire entre OG' et OG
                test_octa=sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[k]))
                if test_octa < 0 :  
                    octaedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)


    # =============================================================================
    def add_to_queue(self,op):
        self.operations_queue.append(op)
    # =============================================================================
    def pygame_quit(self,args):
        pygame.quit()
        quit()
    # =============================================================================
    def restore_axes(self,args):
        glLoadIdentity()
        gluPerspective(45, self.ratio, 0.1, 50.0)
        glTranslatef(0.0,0.0, -8) 

    # =============================================================================
    def gerer_affichage(self,gestion):
        
        # Les rotations s'effectuent par rapport aux axes du tétraèdre de référence
        hu=Operation(name='haut',vecteur= sommets_tetraedre[0],ligne='up',sens=-1)
        hm=Operation(name='haut',vecteur= sommets_tetraedre[0],ligne='middle',sens=-1)
        hd=Operation(name='haut',vecteur= sommets_tetraedre[0],ligne='down',sens=-1)
        gu=Operation(name='gauche',vecteur=sommets_tetraedre[1],ligne='up',sens=-1)
        gm=Operation(name='gauche',vecteur=sommets_tetraedre[1],ligne='middle',sens=-1)
        gd=Operation(name='gauche',vecteur=sommets_tetraedre[1],ligne='down',sens=-1)
        du=Operation(name='droite',vecteur=sommets_tetraedre[2],ligne='up',sens=-1)
        dm=Operation(name='droite',vecteur=sommets_tetraedre[2],ligne='middle',sens=-1)
        dd=Operation(name='droite',vecteur=sommets_tetraedre[2],ligne='down',sens=-1)
        fu=Operation(name='fond',vecteur=sommets_tetraedre[3],ligne='up',sens=-1)
        fm=Operation(name='fond',vecteur=sommets_tetraedre[3],ligne='middle',sens=-1)
        fd=Operation(name='fond',vecteur=sommets_tetraedre[3],ligne='down',sens=-1)

        # définitions des touches clavier pour les opérations/transformations du tetrèdre 
        gestion.add_key("e",self.add_to_queue,hu)
        gestion.add_key("s",self.add_to_queue,hm)
        gestion.add_key("y",self.add_to_queue,hd)
        gestion.add_key("r",self.add_to_queue,gu)
        gestion.add_key("d",self.add_to_queue,gm)
        gestion.add_key("x",self.add_to_queue,gd)
        gestion.add_key("t",self.add_to_queue,du)
        gestion.add_key("f",self.add_to_queue,dm)
        gestion.add_key("c",self.add_to_queue,dd)
        gestion.add_key("z",self.add_to_queue,fu)
        gestion.add_key("g",self.add_to_queue,fm)
        gestion.add_key("v",self.add_to_queue,fd)
        gestion.add_key("a",self.restore_axes,None)
        gestion.add_key("q",self.pygame_quit,None)


if __name__=='__main__':

    separator=60*"="
    print(separator)
    print("Bloc testant la classe Rubik's cube")
    print("affichage et gestion du clavier ")
    print(separator)
    print("                                ")
    print("              A                 ")
    print("             /|\                ")
    print("            / | \               ")
    print("           /  D  \              ")
    print("          B-------C             ")
    print("                                ")
    print("rotation autour des axes passant")
    print("par le centre de gravité (G) et ")
    print("les sommets du tetraèdre        ")
    print()
    print(" touches : ")
    print(" [esy]   : rotation autour de GA")
    print(" [rdx]   : rotation autour de GB")
    print(" [tfc]   : rotation autour de GC")
    print(" [zgv]   : rotation autour de GD")
    print(" [q]     : quitter")
    print()
    print(separator)
    # pygame
    pygame.init()
    display = (600,600)
    infopygame = pygame.display.Info()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (infopygame.current_w,infopygame.current_h)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    # fmv : en fait cette valeur est bien trop basse à 1
    # vitesse de rotation de la caméra
    pas_rotation_camera = 10 
    # Pour tester quand une opération est complète; voir ci-après
    taux_transition_operation = 0 
    # pas de rotation pour les operations 10% 
    # fmv : 20% c'est pas mal chez moi
    # correspond à la varible u dans transformer_rubik
    pas_rotation_operation = 0.2


    # classe gestion clavier global qq soit le polyedre
    gestion_clavier=Gestion_clavier()

    # instanciation du Rubik_cube
    rubik_tetrahedron = Rubik_tetrahedron(ratio=display[0]/display[1])
    rubik_tetrahedron.gerer_affichage(gestion_clavier)
    # pyOpenGl
    gluPerspective(45, rubik_tetrahedron.ratio, 0.1, 50.0)
    glTranslatef(0.0,0.0, -8) 
    glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets


    # ===================
    #   main event loop
    # ===================
    while True:

        # Gestion des événements clavier
        for event in pygame.event.get(): gestion_clavier.check_event_key(event)
        
        # Mouvements de la caméra
        if gestion_clavier.fleche_gauche: glRotatef(pas_rotation_camera, 0, 1, 0)
        if gestion_clavier.fleche_droite: glRotatef(-pas_rotation_camera, 0, 1, 0)
        if gestion_clavier.fleche_haut:   glRotatef(pas_rotation_camera, 1, 0, 0)
        if gestion_clavier.fleche_bas:    glRotatef(-pas_rotation_camera, 1, 0, 0)
        if gestion_clavier.touche_p:      glRotatef(pas_rotation_camera, 0, 0, 1)
        if gestion_clavier.touche_m:      glRotatef(-pas_rotation_camera, 0, 0, 1)
       

        # ======================================
        # Gestion des animations des opérations
        # ======================================
        if taux_transition_operation == 0:
            # Si une opération est dans la queue
            if(len(rubik_tetrahedron.operations_queue) > 0): 
                operation_courante = rubik_tetrahedron.operations_queue.pop(0)
                taux_transition_operation += pas_rotation_operation
        # >= (1 + pas_rotation_camera) en réalité, mais on gagne un calcul
        elif taux_transition_operation >= 1.+pas_rotation_operation:
            # Plus besoin de tourner, la transformation est finie
            taux_transition_operation = 0 
        else:
            rubik_tetrahedron.transformer_rubik(op=operation_courante,u=pas_rotation_operation)
            taux_transition_operation += pas_rotation_operation

        # Mise à jour de l'affichage
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        rubik_tetrahedron.afficher()
        pygame.display.flip()

        #pygame.time.wait(10) # Enlevable


