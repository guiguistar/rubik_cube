#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np

# Couleurs
# NROJWBV
# fmv : ceux sont les vrais couleurs du rubik ?
# fmv : sur mon ecran c'est moche ;)
couleurs_rubik = [
    [ 50./255.,  50./255.,  50./255.], # '#000000'  # Noir    #0
    [196./255.,  30./255.,  58./255.], # '#C41E3A', # Rouge   #1
    [255./255.,  88./255.,   0./255.], # '#FF5800', # Orange  #2 
    [255./255., 218./255.,   0./255.], # '#FFDA00', # Jaune   #3 
    [240./255., 240./255., 240./255.], # '#FFFFFF', # Blanc   #4
    [  0./255.,  81./255., 186./255.], # '#0051BA', # Bleu    #5
    [  1./255., 158./255.,  60./255.]  # '#019E60', # Vert    #6
]


# =============================================================================
#                        CUBE
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

# fmv : oui autant remplacer les 1 par une valeur d'indice du tableau precedent 
# fmv : 0 c'est un peu plus visiuel que 6 ;)
couleurs_faces_aretes_cube = [
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
couleurs_faces_coins_cube = [
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
couleurs_faces_faces_cube = [
    [1,0,0,0,0,0],
    [0,2,0,0,0,0],
    [0,0,3,0,0,0],
    [0,0,0,4,0,0],
    [0,0,0,0,5,0],
    [0,0,0,0,0,6]
]

# =============================================================================
#                                 TETRAHEDRON 
# =============================================================================


# Longeur des axes du repère orthonormé
longueur_axes = 2

#-------------------------------------#
# Listes de points des figures utiles #
#-------------------------------------#

# Le repère orthonormé
sommets_repere = [ [0,0,0], [longueur_axes,0,0], [0,longueur_axes,0], [0,0,longueur_axes] ]
aretes_repere = [[0,1], [0,2], [0,3]]

# ---------------------------#
# Tétraèdre de référence: contexte pour y voir clair #
# -------------------------- #
# On note ABCD le tétraèdre régulier dont:
#
#        A           0 
#       /|\         /|\
#      / D \       / 3 \
#     B-----C     1-----2
#
#
#  -le coté a pour longueur 1
#  -le centre de gravité G est condondu avec l'origine du repère (O,i,j,k)
#  -(BD) // Ox et vecteur GA et j colinéaire de même sens
# La hauteur de BDC issue de D coupe (BC) en D'. On note D'' l'intersection entre (AH) et (BDC).
#
# On peut alors prouver que (exercice plus difficile qu'il n'y paraît) que:
#  -DD' = racine(3) / 2
#  -AA'' = racine(2/3)
#  -GA'' = (1/4) * racine(2/3) et GA = (3/4) * racine (2/3)
#  -A''D'' = (1*3) * racine(3)/ et A''D = (2*3) * racine(3) / 2
#
# S'en déduisent les coordonnées de A, B, C et D dans le repère (O,i,j,k) = (G,i,j,k):
# A(0, (3*4) * racine(2/3), 0)
# B(-1/2, -(1/4) * racine (2/3), (1/3) * racine(3) / 2 )
# C(1/2, -(1/4) * racine (2/3), (1/3) * racine(3) / 2 )
# D(0, -(1/4) * racine (2/3), -(2/3) * racine(3) / 2 )

# Les sommets sont des triplets de coordonnées
sommets_tetraedre = [
    [ 0.  ,  0.75 * np.sqrt(2.0/3.), 0.               ], # A ("sommet")
    [-0.5 , -0.25 * np.sqrt(2.0/3.),  np.sqrt(3.) / 6.], # B (avant gauche)
    [ 0.5 , -0.25 * np.sqrt(2.0/3.),  np.sqrt(3.) / 6.], # C (avant droit)
    [ 0.  , -0.25 * np.sqrt(2.0/3.), -np.sqrt(3.) / 3.], # D (fond)
    [ 0.  ,  0.                    , 0.               ]  # Centre de gravité
    ]

# Les arêtes sont des couples de sommets
#        A           0 
#       /|\         /|\
#      / D \       / 3 \
#     B-----C     1-----2
#
aretes_tetraedre = [
    [0,1], [0,2], [0,3], # Arêtes joignant les sommets du triangle de base au "sommet": [AB], [AC] et [AD]
    [1,2], [2,3], [3,1] # Triangle de base: BCD
]
# Les faces sont des triplets de sommets
faces_tetraedre = [
    [0,1,2], [0,2,3], [0,3,1], # ABC, ACD, ADB
    [1,2,3] # Base: BCD
]
couleurs_aretes_tetraedre = [10,10,10,10,10,10,10]
couleurs_faces_aretes_tetraedre = [
        [1,0,6,0],
        [1,5,0,0],
        [0,5,6,0],
        [1,0,0,3],
        [0,5,0,3],
        [0,0,6,3]
        ]
couleurs_faces_coins_tetraedre = [
        [1,5,6,0],
        [1,0,6,3],
        [1,5,0,3],
        [0,5,6,3],
        [0,0,0,0]
        ]
#-------------------------#
# L'octaèdre de référence #
#-------------------------#
#           0
#           |
#         3-|----2
#        /  |   /
#       /      /
#      4------1
#           | 
#           |
#           5 
#
sommets_octaedre = [
    [0., np.sqrt(2.)/2., 0.], # Le "sommet du haut"
    [0.5, 0., 0.5], # Avant droit
    [0.5, 0., -0.5], # Arrière droit
    [-0.5, 0., -0.5], # Arrière gauche
    [-0.5, 0., 0.5], # Avant gauche
    [0., -np.sqrt(2.)/2., 0.], # Le "sommet du bas"
    [0., 0., 0.] # Centre de gravité
]
# Les arêtes sont des couples de sommets
aretes_octaedre = [
    [0,1], [0,2], [0,3], [0,4],
    [1,2], [2,3], [3,4], [4,1],
    [5,1], [5,2], [5,3], [5,4]
]
# Les faces sont des triplets de sommets (triangles)
faces_octaedre = [
    [0,1,2], [0,2,3], [0,3,4], [0,4,1],
    [5,1,2], [5,2,3], [5,3,4], [5,4,1]    
]
#non utilisé
#couleurs_aretes_octaedre = [10,10,10,10,10,10,10,10,10,10,10,10]

couleurs_faces_octaedre=[
        [5,0,6,0,0,0,0,1],
        [0,0,6,0,0,3,0,1],
        [5,0,0,0,0,3,0,1],
        [5,0,6,0,0,3,0,0],
        [0,0,0,0,0,0,0,0]
]
