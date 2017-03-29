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
from rubik import couleurs_rubik,sommets_tetraedre,aretes_tetraedre,faces_tetraedre,couleurs_aretes_tetraedre,sommets_octaedre,faces_octaedre,couleurs_faces_aretes_tetraedre,couleurs_faces_octaedre,couleurs_faces_coins_tetraedre,aretes_octaedre

# =============================================================================
class Rubik_tetrahedron:
    '''
    Classe Rubik_tetrahedron : ... 
    '''

    # =============================================================================
    def __init__(self,ratio):

        self.ratio = ratio
        self.operations_queue=[]

        # Pour écarter un peu les différentes pièces, on les translate un peu plus
        self.coeff_translation = 1.1
       
        # Construction d'un tétraèdre de référence qui servira à tracer les axes de la pyramide
        self.tetraedre_reference = Polyedre(sommets_tetraedre, aretes_tetraedre,faces_tetraedre, couleurs_rubik)

        self.tetraedres = []
            # Tétraèdres des centres des arêtes (translations du tétraèdre de référence par chacun des
            # vecteurs demi-somme de couples d'extrémités; envisager une boucle
            # A faire:
            #  -modifier (mettre en blanc) les couleurs des faces invisibles de certains tétraèdre
            #  -faire en sorte que les instructions tiennent sur une seule ligne

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
        # Envisager une boucle
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
    def rotation_rubik(self, angle, vecteur):
        for octaedre in self.octaedres:
            octaedre.rotation_polyedre(angle, vecteur)
        for tetraedre in self.tetraedres:
            tetraedre.rotation_polyedre(angle, vecteur)
   

    # Pour les méthodes qui suivent et qui permettent de manipuler la pyramide,
    # on teste à chaque fois chacun des 14 polyèdres pour savoir s'ils sont
    # concernés par le mouvement effectué

    # Revoir les tests sur les produits scalaires (cf tranlations pour séparer les pièces
    # font éhouer les dits tests
    
    # Faire tourner les 2 couches du haut
    def Haut(self, u = 1):
        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][1] > 0: # Test sur l'ordonnée du centre de gravité
                tetraedre.haut(u)
        for octaedre in self.octaedres:
            if octaedre.sommets[6][1] > 0: # Idem
                octaedre.haut(u)
    # Faire tourner le petit tétraèdre du haut
    def haut(self, u = 1):
        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][1] > 0 + np.sqrt(2.0/3):
                tetraedre.haut(u)
    # Faire tourner les 2 couches de gauche
    def Gauche(self, u = 1):
        for tetraedre in self.tetraedres:
            if sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[1])) > 0: # Test sur le produit scalaire entre OG' et OG
                tetraedre.gauche(u)
        for octaedre in self.octaedres:
            if sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[1])) > 0: # Idem 
                octaedre.gauche(u)
    # Faire tourner le petit tétraèdre de gauche
    def gauche(self, u = 1):
        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][0] < -0.7:
                tetraedre.gauche(u)
    # Faire tourner les 2 couches de droite
    def Droite(self, u = 1):
        for tetraedre in self.tetraedres:
            if sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[2])) > 0: # Test sur le produit scalaire entre OG' et OG
                tetraedre.droite(u)
        for octaedre in self.octaedres:
            if sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[2])) > 0: # Idem 
                octaedre.droite(u)
    # Faire tourner le petit tétraèdre de droite
    def droite(self, u = 1):
        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][0] > 0.7:
                tetraedre.droite(u)
    # Faire tourner les 2 couches du fond
    def Fond(self, u = 1):
        for tetraedre in self.tetraedres:
            if sum(np.multiply(tetraedre.sommets[4], sommets_tetraedre[3])) > 0: # Test sur le produit scalaire entre OG' et OG
                tetraedre.fond(u)
        for octaedre in self.octaedres:
            if sum(np.multiply(octaedre.sommets[6], sommets_tetraedre[3])) > 0: # Idem 
                octaedre.fond(u)
    # Faire tourner le petit tétraèdre du fond
    def fond(self, u = 1):
        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][2] < -0.7:
                tetraedre.fond(u)

    # =============================================================================
    # op : Objet de la classe Operation :
    #   op.vecteur : vecteur rotation
    #   op.ligne   : up/down
    #   op.sens    : +1,-1 sens de la rotation 
    def transformer_rubik(self, op, u=1) :

        for tetraedre in self.tetraedres:
            if tetraedre.sommets[4][2] < -0.7:
                tetraedre.rotation_polyedre(op.sens*u * 2 * np.pi / 3,op.vecteur)


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
    def gerer_affichage_tetrahedron(self,gestion):
        
        # Les rotations s'effectuent par rapport aux axes du tétraèdre de référence
    #    def haut(self, u = 1):   self.rotation(u * 2 * np.pi / 3, sommets_tetraedre[0])
    #    def fond(self, u = 1):   self.rotation(u * 2 * np.pi / 3, sommets_tetraedre[3])
    #    def gauche(self, u = 1): self.rotation(u * 2 * np.pi / 3, sommets_tetraedre[1])
    #    def droite(self, u = 1): self.rotation(u * 2 * np.pi / 3, sommets_tetraedre[2])
        # on définit les operations sur le rubik accessible par le clavier
#sommets_tetraedre = [
#    [0, 0.75 * np.sqrt(2.0/3), 0], # A ("sommet")
#    [-0.5, -0.25 * np.sqrt(2.0/3), np.sqrt(3) / 6], # B (avant gauche)
#    [0.5, -0.25 * np.sqrt(2.0/3), np.sqrt(3) / 6], # C (avant droit)
#    [0, -0.25 * np.sqrt(2.0/3), -np.sqrt(3) / 3], # D (fond)
#    [0, 0, 0] # Centre de gravité
#]
#sommets_octaedre = [
#    [0, np.sqrt(2)/2, 0], # Le "sommet du haut"
#    [0.5, 0, 0.5], # Avant droit
#    [0.5, 0, -0.5], # Arrière droit
#    [-0.5, 0, -0.5], # Arrière gauche
#    [-0.5, 0, 0.5], # Avant gauche
#    [0, -np.sqrt(2)/2, 0], # Le "sommet du bas"
#    [0, 0, 0] # Centre de gravité
#]
        haut=Operation(name='haut',vecteur= sommets_tetraedre[0],ligne='up',sens=-1)
        gauche=Operation(name='gauche',vecteur=sommets_tetraedre[1],ligne='middle',sens=-1)
        droite=Operation(name='droite',vecteur=sommets_tetraedre[2],ligne='down',sens=-1)
        fond=Operation(name='fond',vecteur=sommets_tetraedre[3],ligne='down',sens=-1)

#        gestion.add_key("e",self.add_to_queue,haut)
        gestion.add_key("s",self.add_to_queue,fond)
#        gestion.add_key("y",self.add_to_queue,gauche)
#        gestion.add_key("r",self.add_to_queue,droite)
        gestion.add_key("a",self.restore_axes,None)
        gestion.add_key("q",self.pygame_quit,None)



if __name__=='__main__':

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
    rubik_tetrahedron.gerer_affichage_tetrahedron(gestion_clavier)
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


