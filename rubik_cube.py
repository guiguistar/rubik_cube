#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pygame
import numpy as np
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

# Warning!
# Il faudrait vraiment plus de dictionnaires dans ce code

#------------------------#
# Transformations utiles #
#------------------------#

# Rotation
# Entrées:
#  -sommet: le point à faire tourner. C'est une liste de trois floats, exemple: sommet = [1,2.5,3]
#  -angle: l'angle en radians (sens trionométrique) de la rotation
#  -vecteur: donne l'axe de la rotation. C'est une liste de trois points.
# Retour:
#  -une liste de trois points contenant les coordonnées de l'image de sommet par la rotation
#
# Voir https://fr.wikipedia.org/wiki/Matrice_de_rotation#En_dimension_trois si besoin
def Rotation(sommet, angle, vecteur):
    c = np.cos(angle)
    s = np.sin(angle)
    norme = np.sqrt(vecteur[0]**2 + vecteur[1]**2 + vecteur[2]**2)

    # [x, y, z] doit être normé
    x = vecteur[0] / norme
    y = vecteur[1] / norme
    z = vecteur[2] / norme
    
    R = [[x**2*(1-c) +   c, x *y*(1-c) - z*s, x *z*(1-c) + y*s],
         [x *y*(1-c) + z*s, y**2*(1-c) + c  , y *z*(1-c) - x*s],
         [x *z*(1-c) - y*s, y *z*(1-c) + x*s, z**2*(1-c) + c]]

    return np.dot(R, np.transpose(sommet))
#-------------#
# Translation #
#-------------#
# Comme la rotation mais en plus simple
def Translation(sommet, vecteur):
    return [sommet[0] + vecteur[0], sommet[1] + vecteur[1], sommet[2] + vecteur[2]]

#-------------------------------------#
# Listes de points des figures utiles #
#-------------------------------------#

# Nom du cube: ABCDEFGH
#  A sommet avant haut gauche
#  B sommet avant haut droit
#  C sommet avant bas droit
#  D sommet avant bas gauche
#  E sommet arrière bas gauche
#  F sommet arrière bas droit
#  G sommet arrière haut droit
#  H sommet arrière haut gauche

# Z -> arrière/avant
# Y -> bas/haut
# X -> gauche/droit
sommets_cube = [
    # Face avant
    [-1, +1, +1],
    [+1, +1, +1],
    [+1, -1, +1],
    [-1, -1, +1],

    # Face arrière
    [-1, -1, -1],
    [+1, -1, -1],
    [+1, +1, -1],
    [-1, +1, -1],

    # Centre de gravité
    [0, 0, 0]
]
# Les arêtes du cube de référence (couples de sommets)
aretes_cube = [
    [0,1], [1,2], [2,3], [3,0],
    [4,5], [5,6], [6,7], [7,4],
    [0,7], [1,6], [2,5], [3,4]
]
# Les faces du cube de référence (quadruplets de sommets)
faces_cube = [
    [0,1,2,3],
    [4,5,6,7],
    [0,1,6,7],
    [4,3,2,5],
    [0,7,4,3],
    [1,6,5,2]
]

# Couleurs
couleurs_rubik_cube = [
    [196.0/255.0, 30.0/255.0, 58.0/255.0], # '#C41E3A', # Rouge
    [255.0/255.0, 88.0/255.0, 0.0/255.0], # '#FF5800', # Orange
    [255.0/255.0, 218.0/255.0, 0.0/255.0], # '#FFDA00', # Jaune
    [240.0/255.0, 240.0/255.0, 240.0/255.0], # '#FFFFFF', # Blanc
    [0.0/255.0, 81.0/255.0, 186.0/255.0], # '#0051BA', # Bleu
    [1.0/255.0, 158.0/255.0, 60.0/255.0], # '#019E60', # Vert
    [50.0/255.0, 50.0/255.0, 50.0/255.0] # '#000000' # Noir
]
couleurs_faces_aretes = [
    [0,6,2,6,6,6],
    [0,6,6,6,6,5],
    [0,6,6,3,6,6],
    [0,6,6,6,4,6],

    [6,1,6,3,6,6],
    [6,1,6,6,6,5],
    [6,1,2,6,6,6],
    [6,1,6,6,4,6],

    [6,6,2,6,4,6],
    [6,6,2,6,6,5],
    [6,6,6,3,6,5],
    [6,6,6,3,4,6]
]
couleurs_faces_coins = [
    [0,6,2,6,4,6],
    [0,6,2,6,6,5],
    [0,6,6,3,6,5],
    [0,6,6,3,4,6],
    [6,1,6,3,4,6],
    [6,1,6,3,6,5],
    [6,1,2,6,6,5],
    [6,1,2,6,4,6],
    [6,6,6,6,6,6] # Cube du centre, invisible
]
couleurs_faces_faces = [
    [0,6,6,6,6,6],
    [6,1,6,6,6,6],
    [6,6,2,6,6,6],
    [6,6,6,3,6,6],
    [6,6,6,6,4,6],
    [6,6,6,6,6,5]
]

# ROJWBV

class Polyedre:
    def __init__(self, # Constructeur de la classe Polyedre
                 sommets, 
                 aretes,
                 faces,
                 couleurs_aretes, # Liste des couleurs des arêtes
                 couleurs_faces, # Liste des couleurs des faces
                 vecteur_position = [0, 0, 0],
                 angle = 0,
                 vecteur_rotation = [0, 0, 1]):
        
        self.sommets = list(sommets_cube) # Attention à cloner la liste (qui est passée par référence)
        self.aretes = aretes
        self.faces = faces
        
        self.couleurs_aretes = couleurs_aretes
        self.couleurs_faces = couleurs_faces

        # Attention ici: la rotation initiale est effectuée avant la translation initiale
        self.rotation(angle, vecteur_rotation)
        self.translation(vecteur_position)
        
        self.sommets_initiaux = list(self.sommets) # Pour afficher les axes du polyèdres

    def afficher_axes(self):
        glBegin(GL_LINES)
        glColor3fv(couleurs_rubik_cube[4])
        for sommet in self.sommets_initiaux:
            glVertex3fv([0,0,0])
            glVertex3fv([10 * coordonnee for coordonnee in sommet])
        glEnd()
    def afficher_aretes(self):
        glBegin(GL_LINES)
        for couleur, arete in enumerate(self.aretes):
            glColor3fv(couleurs_rubik_cube[3])
            for sommet in arete:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    def afficher_faces(self):
        glBegin(GL_QUADS)
        for couleur, face in enumerate(self.faces):
            glColor3fv(couleurs_rubik_cube[self.couleurs_faces[couleur]])
            for sommet in face:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    def afficher(self):
        self.afficher_faces()
        #self.afficher_aretes() # Gagne énormément en fluidité
    def rotation(self, angle, vecteur):
        self.sommets[:] = [Rotation(sommet, angle, vecteur) for sommet in self.sommets]
    def translation(self, vecteur):
        self.sommets[:] = [Translation(sommet, vecteur) for sommet in self.sommets]

class Rubik_Cube:
    def __init__(self):
        self.coeff_translation = 1.1 # Pour écarter un peu les différentes pièces, on les translate un peu plus
        
        # Construction des 27 cubes du Rubik's cube (le cube central est là)
        self.cubes = []
        
        # Cubes au centre des aretes
        for i, arete in enumerate(aretes_cube):
            self.cubes.append(Polyedre(sommets_cube,
                                       aretes_cube,
                                       faces_cube,
                                       [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_aretes[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[arete[0]], sommets_cube[arete[1]])]))

        # Cubes des coins
        # Le sommet d'indice 8 est le centre de garvité
        for i, sommet in enumerate(sommets_cube):
            self.cubes.append(Polyedre(sommets_cube, aretes_cube,
                                       faces_cube,
                                       [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_coins[i],
                                       [2*c * self.coeff_translation for c in sommet]))

        # Cubes des milieux des faces
        for i, face in enumerate(faces_cube):
            self.cubes.append(Polyedre(sommets_cube, aretes_cube,
                                       faces_cube,
                                       [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_faces[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[face[0]], sommets_cube[face[2]])]))
        
    # Afficher la pyramide revient à afficher chacun de ses polyèdres
    def afficher(self):
        for cube in self.cubes:
            cube.afficher()
        # self.cube_reference.afficher_axes()
    # Tourner la pyramide revient à tourner chacun de ses polyèdres
    def rotation(self, angle, vecteur):
        for cube in self.cubes:
            cube.rotation(angle, vecteur)
    
    # Faire tourner la couche du haut
    def haut(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][1] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 1, 0])
    # Faire tourner la couche du bas
    def bas(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][1] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 1, 0])
    # Faire tourner la couche de gauche
    def gauche(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][0] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [1, 0, 0])
    # Faire tourner la couche de droite
    def droite(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][0] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [1, 0, 0])
    # Faire tourner la couche de arriere
    def arriere(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][2] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 0, 1])
    # Faire tourner la couche de avant
    def avant(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][2] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 0, 1])

def gestion_clavier(event, rubik_cube):
    # Méditer sur ces variables globales
    global fleche_gauche, fleche_droite, fleche_haut, fleche_bas, touche_p, touche_m
    global ratio
    if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:  fleche_gauche = True
        if event.key == pygame.K_RIGHT: fleche_droite = True
        if event.key == pygame.K_UP:    fleche_haut = True
        if event.key == pygame.K_DOWN:  fleche_bas = True
        if event.key == pygame.K_p:     touche_p = True
        if event.key == pygame.K_m:     touche_m = True
                    
        if event.key == pygame.K_a:
            glLoadIdentity()
            gluPerspective(45, ratio, 0.1, 50.0)
            glTranslatef(0.0,0.0, -30) 
            
        if event.key == pygame.K_e: file_operations.append(rubik_cube.haut)
        if event.key == pygame.K_s: file_operations.append(rubik_cube.gauche)
        if event.key == pygame.K_c: file_operations.append(rubik_cube.bas)
        if event.key == pygame.K_f: file_operations.append(rubik_cube.droite)
        if event.key == pygame.K_g: file_operations.append(rubik_cube.avant)
        if event.key == pygame.K_v: file_operations.append(rubik_cube.arriere)

    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:  fleche_gauche = False
        if event.key == pygame.K_RIGHT: fleche_droite = False
        if event.key == pygame.K_UP:    fleche_haut = False
        if event.key == pygame.K_DOWN:  fleche_bas = False
        if event.key == pygame.K_p:     touche_p = False
        if event.key == pygame.K_m:     touche_m = False

def main():
    # Instanciation du repère et de la rubik_cube
    mon_rubik_cube = Rubik_Cube()
    #mon_cube = Polyedre(sommets_cube, aretes_cube, faces_cube, [0,0,0,0,0,0,0,0,0,0,0,0], [0,1,2,3,4,5]);
    
    # Clavier (touches pour faire tourner la caméra)
    global fleche_gauche, fleche_droite, fleche_haut, fleche_bas, touche_p, touche_m
    
    fleche_gauche = False
    fleche_droite = False
    fleche_haut = False
    fleche_bas = False
    touche_p = False
    touche_m = False

    pas_rotation_camera = 1 # ~vitesse de rotation de la caméra
    
    # Transition des opérations
    # Clarifier le nom des variables

    global file_operations
    
    file_operations = [] # Liste qui sert de file pour les différentes opérations (Haut, droite, ...)
    taux_transition_operation = 0 # Pour tester quand une opération est complète; voir ci-après
    pas_rotation_operation = 0.1 # pas pour les opérations

    # pygame
    display = (600,600)
    global ratio
    ratio = display[0]/display[1]

    pygame.init()
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    # pyOpenGl
    gluPerspective(45, ratio, 0.1, 50.0)
    glTranslatef(0.0,0.0, -30) 
    glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets

    while True:
        # Gestion des événements clavier
        for event in pygame.event.get(): gestion_clavier(event, mon_rubik_cube)
        #for event in pygame.event.get(): gestion_clavier(event, mon_cube)
        
        # Mouvements de la caméra
        if fleche_gauche: glRotatef(pas_rotation_camera, 0, 1, 0)
        if fleche_droite: glRotatef(-pas_rotation_camera, 0, 1, 0)
        if fleche_haut:   glRotatef(pas_rotation_camera, 1, 0, 0)
        if fleche_bas:    glRotatef(-pas_rotation_camera, 1, 0, 0)
        if touche_p:      glRotatef(pas_rotation_camera, 0, 0, 1)
        if touche_m:      glRotatef(-pas_rotation_camera, 0, 0, 1)
        
        # Gestion des animations des opérations
        if taux_transition_operation == 0:
            if(len(file_operations) > 0): # Si une opération est dans la file
                operation_courante = file_operations.pop(0)
                taux_transition_operation += pas_rotation_operation
        elif taux_transition_operation > 1.05: # >= (1 + pas_rotation_camera) en réalité, mais on gagne un calcul
            taux_transition_operation = 0 # Plus besoin de tourner, la transformation est finie
        else:
            operation_courante(pas_rotation_operation)
            taux_transition_operation += pas_rotation_operation

        # Mise à jour de l'affichage
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #mon_cube.afficher()
        mon_rubik_cube.afficher()
        pygame.display.flip()

        pygame.time.wait(10) # Enlevable
main()
