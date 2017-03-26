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
from rubik import aretes_cube, sommets_cube, faces_cube, couleurs_faces_aretes_cube, couleurs_faces_coins_cube, couleurs_faces_faces_cube

# =============================================================================
class Rubik_cube:
    '''
    Classe Rubik_cube : ... 
    '''

    # =============================================================================
    def __init__(self,ratio):

        self.ratio = ratio
        self.operations_queue=[]

        # Pour écarter un peu les différentes pièces, on les translate un peu plus
        self.coeff_translation = 1.1 
        
        # Construction des 27 cubes du Rubik's cube (le cube central est là)
        self.cubes = []
        
        # Cubes au centre des aretes (12)
        for i, arete in enumerate(aretes_cube):
            self.cubes.append(Polyedre(sommets_cube,
                                       faces_cube,
                                       couleurs_faces_aretes_cube[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[arete[0]], sommets_cube[arete[1]])]))

        # Cubes des coins (8) + le sommet d'indice 8 qui est le centre de garvité
        for i, sommet in enumerate(sommets_cube):
            # pas le centre de gravité
            if i != 8 :
                self.cubes.append(Polyedre(sommets_cube, 
                                           faces_cube,
                                           couleurs_faces_coins_cube[i],
                                           [2*c * self.coeff_translation for c in sommet]))

        # Cubes des milieux des faces
        for i, face in enumerate(faces_cube):
            self.cubes.append(Polyedre(sommets_cube, 
                                       faces_cube,
                                       couleurs_faces_faces_cube[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[face[0]], sommets_cube[face[2]])]))
        
    # =============================================================================
    # Afficher le rubik revient à afficher chacun de ses cubes 
    def afficher(self):
        for cube in self.cubes:
            cube.afficher()
        #self.cube_reference.afficher_axes() # encore besoin ?

    # =============================================================================
    # Tourner le rubik revient à tourner chacun de ses cubes
    # fmv : n'est pas/plus utilisé
    def rotation_rubik(self, angle, vecteur):
        for cube in self.cubes:
            cube.rotation_polyedre(angle, vecteur)
   
    # =============================================================================
    # op : Objet de la classe Operation :
    #   op.vecteur : vecteur rotation
    #   op.ligne   : up/down
    #   op.sens    : +1,-1 sens de la rotation 
    def transformer_rubik(self, op, u=1) :
       
        # on determine k : l'indice non nul du vecteur de rotation
        for i,e in enumerate(op.vecteur) :
            if e != 0 : 
                k=i
        if op.ligne == 'up' :
            for cube in self.cubes:
                if cube.sommets[8][k] > self.coeff_translation:
                    cube.rotation_polyedre(op.sens * u * np.pi / 2, op.vecteur)
        if op.ligne == 'down' :
            for cube in self.cubes:
                if cube.sommets[8][k] < -self.coeff_translation:
                    cube.rotation_polyedre(op.sens * u * np.pi / 2, op.vecteur)
        if op.ligne == 'middle' :
            for cube in self.cubes:
                if cube.sommets[8][k] > -self.coeff_translation and cube.sommets[8][k] < self.coeff_translation:
                    cube.rotation_polyedre(op.sens * u * np.pi / 2, op.vecteur)

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
        glTranslatef(0.0,0.0, -30) 

    # =============================================================================
    # fmv : À mon avis, les variables globales peuvent etre exprimées dans la classe rubik_cube ...
    # fmv : l'affichage du rubik_cube est alors une methode de la classe
    # fmv : ou alors construire une parenté entre deux classes ( affichage et rubik ) 
    def gerer_affichage_cube(self,gestion):
        
        # on définit les operations sur le rubik accessible par le clavier
        haut=Operation(name='haut',vecteur=[0,1,0],ligne='up',sens=-1)
        bas=Operation(name='bas',vecteur=[0,1,0],ligne='down',sens=-1)
        hbm=Operation(name='hbm',vecteur=[0,1,0],ligne='middle',sens=-1)
        gauche=Operation(name='gauche',vecteur=[1,0,0],ligne='up',sens=-1)
        droite=Operation(name='droite',vecteur=[1,0,0],ligne='down',sens=-1)
        gdm=Operation(name='gdm',vecteur=[1,0,0],ligne='middle',sens=-1)
        arriere=Operation(name='arriere',vecteur=[0,0,1],ligne='up',sens=-1)
        avant=Operation(name='avant',vecteur=[0,0,1],ligne='down',sens=-1)
        aam=Operation(name='aam',vecteur=[0,0,1],ligne='middle',sens=-1)

        gestion.add_key("e",self.add_to_queue,haut)
        gestion.add_key("s",self.add_to_queue,hbm)
        gestion.add_key("y",self.add_to_queue,bas)
        gestion.add_key("r",self.add_to_queue,gauche)
        gestion.add_key("d",self.add_to_queue,gdm)
        gestion.add_key("x",self.add_to_queue,droite)
        gestion.add_key("t",self.add_to_queue,avant)
        gestion.add_key("f",self.add_to_queue,aam)
        gestion.add_key("c",self.add_to_queue,arriere)
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
    pas_rotation_camera = 10 # ~vitesse de rotation de la caméra
    # Pour tester quand une opération est complète; voir ci-après
    taux_transition_operation = 0 
    # pas de rotation pour les operations 10% 
    # fmv : 20% c'est pas mal chez moi
    # correspond à la varible u dans transformer_rubik
    pas_rotation_operation = 0.2


    # classe gestion clavier global qq soit le polyedre
    gestion_clavier=Gestion_clavier()

    # instanciation du Rubik_cube
    rubik_cube = Rubik_cube(ratio=display[0]/display[1])
    rubik_cube.gerer_affichage_cube(gestion_clavier)
    # pyOpenGl
    gluPerspective(45, rubik_cube.ratio, 0.1, 50.0)
    glTranslatef(0.0,0.0, -30) 
    glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets


    # ===================
    #   main event loop
    # ===================
    while True:

        # Gestion des événements clavier
        #for event in pygame.event.get(): rubik_cube.gestion_clavier(event)
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
            if(len(rubik_cube.operations_queue) > 0): 
                operation_courante = rubik_cube.operations_queue.pop(0)
                taux_transition_operation += pas_rotation_operation
        # >= (1 + pas_rotation_camera) en réalité, mais on gagne un calcul
        elif taux_transition_operation > 1.05:
            # Plus besoin de tourner, la transformation est finie
            taux_transition_operation = 0 
        else:
            rubik_cube.transformer_rubik(op=operation_courante,u=pas_rotation_operation)
            taux_transition_operation += pas_rotation_operation

        # Mise à jour de l'affichage
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        rubik_cube.afficher()
        pygame.display.flip()

        #pygame.time.wait(10) # Enlevable


