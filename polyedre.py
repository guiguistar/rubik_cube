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

from rubik import couleurs_rubik

# =============================================================================
class Polyedre:
    '''
    Classe Polyedre : ... 
    '''

    # =============================================================================
    def __init__(self, 
                 sommets, 
                 faces,
                 couleurs_faces, # Liste des couleurs des faces
                 vecteur_position = [0, 0, 0],
                 angle = 0,
                 vecteur_rotation = [0, 0, 1]):
       
        # Attention à cloner la liste (qui est passée par référence)
        self.sommets = list(sommets) 
        self.faces = faces
        
        self.couleurs_faces = couleurs_faces

        # Attention ici: la rotation initiale est effectuée avant la translation initiale
        # fmv : pourquoi ?
        self.rotation_polyedre(angle, vecteur_rotation)
        self.translation_polyedre(vecteur_position)
       
        # fmv : ?? ce commentaire
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
            glColor3fv(couleurs_rubik[3])
            for sommet in arete:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    # =============================================================================
    def afficher_faces(self):
        glBegin(GL_QUADS)
        for couleur, face in enumerate(self.faces):
            glColor3fv(couleurs_rubik[self.couleurs_faces[couleur]])
            for sommet in face:
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
        self.sommets[:] = [translation(sommet, vecteur) for sommet in self.sommets]

if __name__=='__main__':

    # pygame
    pygame.init()
    display = (600,600)
    infopygame = pygame.display.Info()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (infopygame.current_w,infopygame.current_h)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    #fmv : creer un test avec un simple polyedre.

    # ===================
    #   main event loop
    # ===================
    #while True:




