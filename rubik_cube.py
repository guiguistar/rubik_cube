#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pygame
import numpy as np
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

# =============================================================================
# Warning!
# Il faudrait vraiment plus de dictionnaires dans ce code
# fmv : je suis d'accord avec ce warning !
# =============================================================================

# ========================
# Transformations utiles #
# ========================


# =============================================================================
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
# =============================================================================
# Translation #
# Comme la rotation mais en plus simple
def Translation(sommet, vecteur):
    return [sommet[0] + vecteur[0], sommet[1] + vecteur[1], sommet[2] + vecteur[2]]




# =============================================================================
# Listes de points des figures utiles #
#
# Nom du cube: ABCDEFGH
# 
#  A sommet avant haut gauche
#  B sommet avant haut droit
#  C sommet avant bas droit
#  D sommet avant bas gauche
#  E sommet arrière bas gauche
#  F sommet arrière bas droit
#  G sommet arrière haut droit
#  H sommet arrière haut gauche
#
#      H-----G        7-----6
#     /|    /|       /|    /|
#    A-----B |      0-----1 |  
#    | E---|-F      | 4---|-5  
#    |/    |/       |/    |/
#    D-----C        3-----2
#
#
# Z -> arrière/avant
# Y -> bas/haut
# X -> gauche/droit
#
#              Y
# 
#              |
#              |  
#              |----- X
#             /
#            /
#           Z
#


# fmv : tous ces tableaux peuvent etre définis dans les classes Polyedre ou Rubik_cube 
# fmv : si je me trompe pas ils ne sont jamais utilisés à l'exterieur 
sommets_cube = [
    # Face avant
    [-1, +1, +1], #0 A
    [+1, +1, +1], #1 B
    [+1, -1, +1], #2 C
    [-1, -1, +1], #3 D

    # Face arrière
    [-1, -1, -1], #4 E
    [+1, -1, -1], #5 F
    [+1, +1, -1], #6 G
    [-1, +1, -1], #7 H

    # Centre de gravité
    [0, 0, 0]     #8 O
]
#
# Les arêtes du cube de référence (couples de sommets)
#      H-----G        7-----6
#     /|    /|       /|    /|
#    A-----B |      0-----1 |  
#    | E---|-F      | 4---|-5  
#    |/    |/       |/    |/
#    D-----C        3-----2
#
aretes_cube = [
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
#
# Les faces du cube de référence (quadruplets de sommets)
#      H-----G        7-----6
#     /|    /|       /|    /|
#    A-----B |      0-----1 |  
#    | E---|-F      | 4---|-5  
#    |/    |/       |/    |/
#    D-----C        3-----2
faces_cube = [
    [0,1,2,3], #ABCD  avant
    [4,5,6,7], #EFGH  arriere
    [0,1,6,7], #ABGH  haut
    [4,3,2,5], #EDCF  bas
    [0,7,4,3], #AHED  gauche
    [1,6,5,2]  #BGFC  droite
]

# Couleurs
# NROJWBV
# fmv : ceux sont les vrais couleurs du rubik ?
# fmv : sur mon ecran c'est moche ;)
couleurs_rubik_cube = [
    [ 50./255.,  50./255.,  50./255.], # '#000000'  # Noir
    [196./255.,  30./255.,  58./255.], # '#C41E3A', # Rouge
    [255./255.,  88./255.,   0./255.], # '#FF5800', # Orange
    [255./255., 218./255.,   0./255.], # '#FFDA00', # Jaune
    [240./255., 240./255., 240./255.], # '#FFFFFF', # Blanc
    [  0./255.,  81./255., 186./255.], # '#0051BA', # Bleu
    [  1./255., 158./255.,  60./255.]  # '#019E60', # Vert
]
# fmv : oui autant remplacer les 1 par une valeur d'indice du tableau precedent 
# fmv : 0 c'est un peu plus visiuel que 6 ;)
couleurs_faces_aretes = [
    [1,0,3,0,0,0],
    [1,0,0,0,0,6],
    [1,0,0,4,0,0],
    [1,0,0,0,5,0],

    [0,2,0,4,0,0],
    [0,2,0,0,0,6],
    [0,2,3,0,0,0],
    [0,2,0,0,5,0],

    [0,0,3,0,5,0],
    [0,0,3,0,0,6],
    [0,0,0,4,0,6],
    [0,0,0,4,5,0]
]
couleurs_faces_coins = [
    [1,0,3,0,5,0],
    [1,0,3,0,0,6],
    [1,0,0,4,0,6],
    [1,0,0,4,5,0],
    [0,2,0,4,5,0],
    [0,2,0,4,0,6],
    [0,2,3,0,0,6],
    [0,2,3,0,5,0],
    [0,0,0,0,0,0] # Cube du centre, invisible
]
couleurs_faces_faces = [
    [1,0,0,0,0,0],
    [0,2,0,0,0,0],
    [0,0,3,0,0,0],
    [0,0,0,4,0,0],
    [0,0,0,0,5,0],
    [0,0,0,0,0,6]
]


# =============================================================================
# =============================================================================

class Polyedre:
    '''
    Classe Polyedre : ... 
    '''
    # =============================================================================
    def __init__(self, 
                 sommets, 
   #              aretes,
                 faces,
   #              couleurs_aretes, # Liste des couleurs des arêtes
                 couleurs_faces, # Liste des couleurs des faces
                 vecteur_position = [0, 0, 0],
                 angle = 0,
                 vecteur_rotation = [0, 0, 1]):
       
        # Attention à cloner la liste (qui est passée par référence)
        self.sommets = list(sommets_cube) 

        #self.aretes = aretes
        self.faces = faces
        
        #self.couleurs_aretes = couleurs_aretes
        self.couleurs_faces = couleurs_faces

        # Attention ici: la rotation initiale est effectuée avant la translation initiale
        # fmv : pourquoi ?
        self.rotation(angle, vecteur_rotation)
        self.translation(vecteur_position)
        
        self.sommets_initiaux = list(self.sommets) # Pour afficher les axes du polyèdres

    # =============================================================================
    def afficher_axes(self):
        glBegin(GL_LINES)
        glColor3fv(couleurs_rubik_cube[4])
        for sommet in self.sommets_initiaux:
            glVertex3fv([0,0,0])
            glVertex3fv([10 * coordonnee for coordonnee in sommet])
        glEnd()
    # =============================================================================
    def afficher_aretes(self):
        glBegin(GL_LINES)
        for couleur, arete in enumerate(self.aretes):
            glColor3fv(couleurs_rubik_cube[3])
            for sommet in arete:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    # =============================================================================
    def afficher_faces(self):
        glBegin(GL_QUADS)
        for couleur, face in enumerate(self.faces):
            glColor3fv(couleurs_rubik_cube[self.couleurs_faces[couleur]])
            for sommet in face:
                glVertex3fv(self.sommets[sommet])
        glEnd()
    # =============================================================================
    def afficher(self):
        self.afficher_faces()
        #self.afficher_aretes() # Gagne énormément en fluidité
    # =============================================================================
    def rotation(self, angle, vecteur):
        self.sommets[:] = [Rotation(sommet, angle, vecteur) for sommet in self.sommets]
    # =============================================================================
    def translation(self, vecteur):
        self.sommets[:] = [Translation(sommet, vecteur) for sommet in self.sommets]

class Rubik_Cube:
    '''
    Classe Rubik_Cube : ... 
    '''

    # =============================================================================
    def __init__(self,ratio):
        self.ratio = ratio
        self.file_operations=[]
        # Pour écarter un peu les différentes pièces, on les translate un peu plus
        self.coeff_translation = 1.05 
        
        # Construction des 27 cubes du Rubik's cube (le cube central est là)
        self.cubes = []
        
        # Cubes au centre des aretes (12)
        for i, arete in enumerate(aretes_cube):
            self.cubes.append(Polyedre(sommets_cube,
        #                               aretes_cube,
                                       faces_cube,
        #                               [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_aretes[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[arete[0]], sommets_cube[arete[1]])]))

        # Cubes des coins (8) + le sommet d'indice 8 qui est le centre de garvité
        for i, sommet in enumerate(sommets_cube):
            self.cubes.append(Polyedre(sommets_cube, 
        #                               aretes_cube,
                                       faces_cube,
        #                               [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_coins[i],
                                       [2*c * self.coeff_translation for c in sommet]))

        # Cubes des milieux des faces
        for i, face in enumerate(faces_cube):
            self.cubes.append(Polyedre(sommets_cube, 
        #                               aretes_cube,
                                       faces_cube,
        #                               [7,7,7,7,7,7,7,7,7,7,7,7,7],
                                       couleurs_faces_faces[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[face[0]], sommets_cube[face[2]])]))
        
    # =============================================================================
    # Afficher le rubik revient à afficher chacun de ses cubes 
    def afficher(self):
        for cube in self.cubes:
            cube.afficher()
        # self.cube_reference.afficher_axes()

    # =============================================================================
    # Tourner le rubik revient à tourner chacun de ses cubes
    def rotation(self, angle, vecteur):
        for cube in self.cubes:
            cube.rotation(angle, vecteur)
   
    # =============================================================================
    # possible modif fmv : 
    # une fonction pour toute 
    # vecteur : vecteur rotation
    # spin    : + ou - up/down
    # probleme je n'arrive pas à comprendre comment se comporte u dans cette fonction ?
    # u disparait de l'appel des fonctions haut,bas,... ci dessous dans la fonction main
    def tourner_couche(self, u=1, vecteur=[1,0,0] , spin='+' ) :
        for i,e in enumerate(vecteur) :
            if e != 0 : 
                k=i
        print k
        if spin == '+' :
            for cube in self.cubes:
                if cube.sommets[8][k] > self.coeff_translation:
                    cube.rotation(-u * np.pi / 2, vecteur)
        if spin == '-' :
            for cube in self.cubes:
                if cube.sommets[8][k] < -self.coeff_translation:
                    cube.rotation(-u * np.pi / 2, vecteur)

    # =============================================================================
    # Faire tourner la couche du haut
    def haut(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][1] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 1, 0])
    # =============================================================================
    # Faire tourner la couche du bas
    def bas(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][1] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 1, 0])
    # =============================================================================
    # Faire tourner la couche de gauche
    def gauche(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][0] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [1, 0, 0])
    # =============================================================================
    # Faire tourner la couche de droite
    def droite(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][0] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [1, 0, 0])
    # =============================================================================
    # Faire tourner la couche de arriere
    def arriere(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][2] < -self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 0, 1])
    # =============================================================================
    # Faire tourner la couche de avant
    def avant(self, u = 1):
        for cube in self.cubes:
            if cube.sommets[8][2] > self.coeff_translation:
                cube.rotation(-u * np.pi / 2, [0, 0, 1])
    # =============================================================================
    # fmv : À mon avis, les variables globales peuvent etre exprimées dans la classe rubik_cube ...
    # fmv : l'affichage du rubik_cube est alors une methode de la classe
    # fmv : ou alors construire une parenté entre deux classes ( affichage et rubik ) 
    def gestion_clavier(self,event, rubik_cube):
        # Méditer sur ces variables globales
   #     global fleche_gauche, fleche_droite, fleche_haut, fleche_bas, touche_p, touche_m
    #    global ratio
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  self.fleche_gauche = True
            if event.key == pygame.K_RIGHT: self.fleche_droite = True
            if event.key == pygame.K_UP:    self.fleche_haut = True
            if event.key == pygame.K_DOWN:  self.fleche_bas = True
            if event.key == pygame.K_p:     self.touche_p = True
            if event.key == pygame.K_m:     self.touche_m = True
                        
            if event.key == pygame.K_a:
                glLoadIdentity()
                gluPerspective(45, self.ratio, 0.1, 50.0)
                glTranslatef(0.0,0.0, -30) 
                
            if event.key == pygame.K_e: self.file_operations.append(rubik_cube.haut)
            if event.key == pygame.K_s: self.file_operations.append(rubik_cube.gauche)
            if event.key == pygame.K_c: self.file_operations.append(rubik_cube.bas)
            if event.key == pygame.K_f: self.file_operations.append(rubik_cube.droite)
            if event.key == pygame.K_g: self.file_operations.append(rubik_cube.avant)
            if event.key == pygame.K_v: self.file_operations.append(rubik_cube.arriere)

            #if event.key == pygame.K_e: file_operations.append(rubik_cube.tourner_couche([0,1,0],'+'))
            #if event.key == pygame.K_s: file_operations.append(rubik_cube.tourner_couche([0,1,0],'-'))
            #if event.key == pygame.K_c: file_operations.append(rubik_cube.tourner_couche([1,0,0],'+'))
            #if event.key == pygame.K_f: file_operations.append(rubik_cube.tourner_couche([1,0,0],'-'))
            #if event.key == pygame.K_g: file_operations.append(rubik_cube.tourner_couche([0,0,1],'+'))
            #if event.key == pygame.K_v: file_operations.append(rubik_cube.tourner_couche([0,0,1],'-'))

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:  self.fleche_gauche = False
            if event.key == pygame.K_RIGHT: self.fleche_droite = False
            if event.key == pygame.K_UP:    self.fleche_haut = False
            if event.key == pygame.K_DOWN:  self.fleche_bas = False
            if event.key == pygame.K_p:     self.touche_p = False
            if event.key == pygame.K_m:     self.touche_m = False


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

