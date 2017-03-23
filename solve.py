#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import copy

import random
import pygame
import numpy as np
from pygame.locals import *
from rubik_cube import *

from OpenGL.GL import *
from OpenGL.GLU import *

def test(rubik_cube):
    op1=Operation(name='test',vecteur=[1.,0.,0.],ligne='up',sens=-1.)
    op2=Operation(name='test',vecteur=[1.,0.,0.],ligne='up',sens=1.)
    rubik_cube.operations_queue.append(op1)
    rubik_cube.operations_queue.append(op2)


# ===================================================    
# inverse les operations de transformation du Rubik Cube
# Si la liste des opération est A, B , C ...
# la liste en sortie est donnée par C^-1, B^-1, A^-1
# entrée : liste d'opérations
# sortie : liste des opérations inverses
def inverser(ops):
    inverse=[]
    for op in reversed(ops):
        # deep copy de l'opération
        ip=copy.deepcopy(op)
        # méthode de Operation()
        ip.inverse()
        inverse.append(ip)
    return inverse

# ===================================================    
#  entrée : - rubik_cube : objet rubik 
#           - nop_random : nombre d'operations 
#  sortie : liste des opérations appliqués
#
#  note : la liste en sortie est également ajouté à 
#  la queue des operations de l'objet rubik_cube pour
#  affichage
# ===================================================    
def randomize_cube(rubik_cube,nop_random=10):

    print 60*"="
    print "Mélange rubik_cube avec "+str(nop_random)+" operations"
    print 60*"="
    print 
    # =========================================
    # génerer toutes les operations possibles ( que 18?) 
    # =========================================
    vecteurs=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
    lignes=['up','middle','down']
    rot=[1.,-1.]
    nameop=[]
    nop=len(vecteurs)*len(lignes)*len(rot)
    for name in range(nop):
        nameop.append('op'+str(name))
    iname=0
    operations_random=[]
    for v in vecteurs:
        for s in lignes:
            for r in rot:
                operations_random.append(Operation(name=nameop[iname],vecteur=v,ligne=s,sens=r))
                iname+=1

    print len(operations_random)
    # =========================================
    # choisir au hasard parmis ces 18 operations
    # et 
    all_operations=[]
    iop=0
    while iop < nop_random :
        op=random.choice(operations_random)
        print op
        rubik_cube.operations_queue.append(op)
        all_operations.append(op)
        iop+=1

    return all_operations



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

    # instanciation du Rubik_cube
    rubik_cube = Rubik_Cube(ratio=display[0]/display[1])
    
    # pyOpenGl
    gluPerspective(45, rubik_cube.ratio, 0.1, 50.0)
    glTranslatef(0.0,0.0, -30) 
    glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets

    #test(rubik_cube)

    ops=randomize_cube(rubik_cube,40)
    inversops=inverser(ops)
    for op in inversops:
        print "inverse",op
        rubik_cube.operations_queue.append(op)

    # ===================
    #   main event loop
    # ===================
    while True:

        # Gestion des événements clavier
        for event in pygame.event.get(): rubik_cube.gestion_clavier(event)
        
        # Mouvements de la caméra
        if rubik_cube.fleche_gauche: glRotatef(pas_rotation_camera, 0, 1, 0)
        if rubik_cube.fleche_droite: glRotatef(-pas_rotation_camera, 0, 1, 0)
        if rubik_cube.fleche_haut:   glRotatef(pas_rotation_camera, 1, 0, 0)
        if rubik_cube.fleche_bas:    glRotatef(-pas_rotation_camera, 1, 0, 0)
        if rubik_cube.touche_p:      glRotatef(pas_rotation_camera, 0, 0, 1)
        if rubik_cube.touche_m:      glRotatef(-pas_rotation_camera, 0, 0, 1)

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


