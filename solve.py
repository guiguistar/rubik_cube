#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pygame
import numpy as np
from pygame.locals import *
from rubik_cube import *

from OpenGL.GL import *
from OpenGL.GLU import *


def random_cube():

    pass

def solve_cube():
    pass



if __name__=='__main__':
    # pygame
    display = (600,600)
    mon_rubik_cube = Rubik_Cube(ratio=display[0]/display[1])
    
    # Instanciation du repère et de la rubik_cube
    
    # test : un seul cube
    #mon_cube = Polyedre(sommets_cube, aretes_cube, faces_cube, 
    #[0,0,0,0,0,0,0,0,0,0,0,0], [0,1,2,3,4,5]);
    
    # Clavier (touches pour faire tourner la caméra)
    #global fleche_gauche, fleche_droite, fleche_haut, fleche_bas, touche_p, touche_m
    
    mon_rubik_cube.fleche_gauche = False
    mon_rubik_cube.fleche_droite = False
    mon_rubik_cube.fleche_haut = False
    mon_rubik_cube.fleche_bas = False
    mon_rubik_cube.touche_p = False
    mon_rubik_cube.touche_m = False

    # fmv : en fait cette valeur est bien trop basse à 1
    pas_rotation_camera = 10 # ~vitesse de rotation de la caméra
    
    # Transition des opérations
    # Clarifier le nom des variables

    #global file_operations
    
    #file_operations = [] # Liste qui sert de file pour les différentes opérations (Haut, droite, ...)
    taux_transition_operation = 0 # Pour tester quand une opération est complète; voir ci-après
    pas_rotation_operation = 0.1 # pas pour les opérations

    pygame.init()
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # pyOpenGl
    gluPerspective(45, mon_rubik_cube.ratio, 0.1, 50.0)
    glTranslatef(0.0,0.0, -30) 
    glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets

    while True:
        # Gestion des événements clavier
        for event in pygame.event.get(): mon_rubik_cube.gestion_clavier(event, mon_rubik_cube)
        #for event in pygame.event.get(): mon_rubik_cube.gestion_clavier(event, mon_cube)
        
        # Mouvements de la caméra
        if mon_rubik_cube.fleche_gauche: glRotatef(pas_rotation_camera, 0, 1, 0)
        if mon_rubik_cube.fleche_droite: glRotatef(-pas_rotation_camera, 0, 1, 0)
        if mon_rubik_cube.fleche_haut:   glRotatef(pas_rotation_camera, 1, 0, 0)
        if mon_rubik_cube.fleche_bas:    glRotatef(-pas_rotation_camera, 1, 0, 0)
        if mon_rubik_cube.touche_p:      glRotatef(pas_rotation_camera, 0, 0, 1)
        if mon_rubik_cube.touche_m:      glRotatef(-pas_rotation_camera, 0, 0, 1)
        
        # Gestion des animations des opérations
        if taux_transition_operation == 0:
            if(len(mon_rubik_cube.file_operations) > 0): # Si une opération est dans la file
                operation_courante = mon_rubik_cube.file_operations.pop(0)
                taux_transition_operation += pas_rotation_operation
        elif taux_transition_operation > 1.05: # >= (1 + pas_rotation_camera) en réalité, mais on gagne un calcul
            taux_transition_operation = 0 # Plus besoin de tourner, la transformation est finie
        else:
            operation_courante(pas_rotation_operation)
            taux_transition_operation += pas_rotation_operation

        # Mise à jour de l'affichage
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # test un seul cube 
        # mon_cube.afficher()

        mon_rubik_cube.afficher()
        pygame.display.flip()

        pygame.time.wait(10) # Enlevable

