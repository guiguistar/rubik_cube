#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

import numpy as np

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from pygame_gestion_clavier import Gestion_clavier
from op_transformations import rotation,translation

from rubik_constants import couleurs_rubik

# =============================================================================
class Polyedre:
    '''
    Classe Polyedre : ... 
    '''

    # =============================================================================
    def __init__(self, 
                 sommets, 
                 aretes,
                 faces,
                 couleurs_faces, # Liste des couleurs des faces
                 vecteur_position = [0, 0, 0],
                 angle = 0,
                 vecteur_rotation = [0, 0, 1]):
       
        # Attention à cloner la liste (qui est passée par référence)
        self.sommets = list(sommets) 
        self.aretes  = aretes
        self.faces = faces
        
        self.couleurs_faces = couleurs_faces

        # Attention ici: la rotation initiale est effectuée avant la translation initiale
        self.rotation_polyedre(angle, vecteur_rotation)
        self.translation_polyedre(vecteur_position)
       
        # Pour afficher les axes du polyèdres 
        self.sommets_initiaux = list(self.sommets) 

    # =============================================================================
    def afficher_axes(self):
        glBegin(GL_LINES)
        glColor3fv(couleurs_rubik[4])
        for sommet in self.sommets_initiaux:
            glVertex3fv([0,0,0])
            glVertex3fv([10 * coordonnee for coordonnee in sommet])
        glEnd()
    # =============================================================================
    def afficher_aretes(self):
        glBegin(GL_LINES)
        for couleur, arete in enumerate(self.aretes):
            glColor3fv(couleurs_rubik[0])
            for sommet in arete:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    # =============================================================================
    def afficher_faces(self):
        # fmv : necessaire de savoir quel types de polygones on affiche 
        # fmv : il suffit de déterminer la taille self.faces
        if len(self.faces[0]) == 4 :
            glBegin(GL_QUADS)
        if len(self.faces[0]) == 3 :
            glBegin(GL_TRIANGLES)
        for couleur, face in enumerate(self.faces):
            #print couleur,face,self.couleurs_faces[couleur]
            glColor3fv(couleurs_rubik[self.couleurs_faces[couleur]])
            for sommet in face:
             #   print sommet , self.sommets[sommet]
                glVertex3fv(self.sommets[sommet])
        glEnd()
    # =============================================================================
    def afficher(self):
        self.afficher_faces()
        #self.afficher_aretes() # Gagne énormément en fluidité
    # =============================================================================
    def rotation_polyedre(self, angle, vecteur):
        self.sommets[:] = [rotation(sommet, angle, vecteur) for sommet in self.sommets]
    # =============================================================================
    def translation_polyedre(self, vecteur):
        #print "in translation_polyedre",vecteur
        self.sommets[:] = [translation(sommet, vecteur) for sommet in self.sommets]

if __name__=='__main__':

    # pygame
    pygame.init()
    display = (600,600)
    infopygame = pygame.display.Info()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (infopygame.current_w,infopygame.current_h)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # vitesse de rotation de la caméra
    pas_rotation_camera = 5 

   
    sommets = [
    [-1, +1, +1], 
    [+1, +1, +1], 
    [+1, -1, +1], 
    [-1, -1, +1], 
    [-1, -1, -1], 
    [+1, -1, -1], 
    [+1, +1, -1], 
    [-1, +1, -1]  ]

    aretes = [
    [0,1], #AB
    [1,2], #BC
    [2,3], #CD 
    [3,0], #DA
    [4,5], #EF 
    [5,6], #FG
    [6,7], #GH
    [7,4], #HE
    [0,7], #AH 
    [1,6], #BG
    [2,5], #CF
    [3,4]  #DE
    ]

    faces = [
    [0,1,2,3], #ABCD  avant
    [4,5,6,7], #EFGH  arriere
    [0,1,6,7], #ABGH  haut
    [4,3,2,5], #EDCF  bas
    [0,7,4,3], #AHED  gauche
    [1,6,5,2]  #BGFC  droite
    ]

    couleurs_faces=[4,4,4,4,4,4]
    # classe gestion clavier global qq soit le polyedre
    gestion_clavier=Gestion_clavier()

    #instanciation de la classe Polyedre
    test = Polyedre(sommets, aretes,faces, couleurs_faces)
    # pyOpenGl
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
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
 

        # Mise à jour de l'affichage
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        test.afficher()
        test.afficher_aretes()
        pygame.display.flip()




