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

# =============================================================================
# Warning!
# Il faudrait vraiment plus de dictionnaires dans ce code
# fmv : je suis d'accord avec ce warning !
# fmv :
# fmv :
# =============================================================================

# ========================
# Transformations utiles #
# ========================

class Operation: 
    '''
    class Operation :
    Cette classe permet de construire une opération de transformation du cube de Rubik
    Chaque transformation est définit par un vecteur x,y,z; une ligne 'up','middle','down' et un sens de 
    rotation + et -

    on définit deux méthodes :
        __repr__ : pour le print de la classe
        inverse  : le sens de rotation de l'opération
    '''
    def __init__(self,name='',vecteur=[1,0,0],ligne='up',sens=1.):

        self.name=name
        self.vecteur=vecteur
        self.ligne=ligne
        self.sens=sens

    def __repr__(self):
        return "{}:  vecteur= {}, ligne= {}, sens= {}".format(self.name,self.vecteur,self.ligne,self.sens)

    def inverse(self):
        self.sens=-self.sens

# =============================================================================
# rotation
# Entrées:
#  -sommet: le point à faire tourner. C'est une liste de trois floats, exemple: sommet = [1,2.5,3]
#  -angle: l'angle en radians (sens trionométrique) de la rotation
#  -vecteur: donne l'axe de la rotation. C'est une liste de trois points.
# Retour:
#  -une liste de trois points contenant les coordonnées de l'image de sommet par la rotation
#
# Voir https://fr.wikipedia.org/wiki/Matrice_de_rotation#En_dimension_trois si besoin
def rotation(sommet, angle, vecteur):
    
    c = np.cos(angle)
    s = np.sin(angle)
    norme = np.sqrt(vecteur[0]**2 + vecteur[1]**2 + vecteur[2]**2)
    
    # [x, y, z] doit être normé
    x = vecteur[0] / norme
    y = vecteur[1] / norme
    z = vecteur[2] / norme
        
    R = [[x**2*(1.-c) +   c, x *y*(1.-c) - z*s, x *z*(1.-c) + y*s],
         [x *y*(1.-c) + z*s, y**2*(1.-c) + c  , y *z*(1.-c) - x*s],
         [x *z*(1.-c) - y*s, y *z*(1.-c) + x*s, z**2*(1.-c) + c]]
    
    return np.dot(R, np.transpose(sommet))
# =============================================================================
# translation #
# Comme la rotation mais en plus simple
def translation(sommet, vecteur):
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
        self.sommets = list(sommets_cube) 

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
    def rotation_polyedre(self, angle, vecteur):
        self.sommets[:] = [rotation(sommet, angle, vecteur) for sommet in self.sommets]
    # =============================================================================
    def translation_polyedre(self, vecteur):
        self.sommets[:] = [translation(sommet, vecteur) for sommet in self.sommets]

# =============================================================================
class Rubik_cube:
    '''
    Classe Rubik_cube : ... 
    '''

    # =============================================================================
    def __init__(self,ratio):

        self.fleche_gauche = False
        self.fleche_droite = False
        self.fleche_haut = False
        self.fleche_bas = False
        self.touche_p = False
        self.touche_m = False
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
                                       couleurs_faces_aretes[i],
                                       [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_cube[arete[0]], sommets_cube[arete[1]])]))

        # Cubes des coins (8) + le sommet d'indice 8 qui est le centre de garvité
        for i, sommet in enumerate(sommets_cube):
            self.cubes.append(Polyedre(sommets_cube, 
                                       faces_cube,
                                       couleurs_faces_coins[i],
                                       [2*c * self.coeff_translation for c in sommet]))

        # Cubes des milieux des faces
        for i, face in enumerate(faces_cube):
            self.cubes.append(Polyedre(sommets_cube, 
                                       faces_cube,
                                       couleurs_faces_faces[i],
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



class Rubik_tetrahedron:

    '''
    Classe Rubik_tetrahedron : ... 
    '''
    def __init__(self,ratio):
    
        # Construction d'un tétraèdre de référence qui servira à tracer les axes de la pyramide
        self.tetraedre_reference = Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre)
        self.coeff_translation = 1.1 # Pour écarter un peu les différentes pièces, on les translate un peu plus
        self.ratio = ratio
        
        # Construction des 10 tétraèdres de la pyramide
        self.tetraedres = [
            # Tétraèdres des centres des arêtes (translations du tétraèdre de référence par chacun des
            # vecteurs demi-somme de couples d'extrémités; envisager une boucle
            # A faire:
            #  -modifier (mettre en blanc) les couleurs des faces invisibles de certains tétraèdre
            #  -faire en sorte que les instructions tiennent sur une seule ligne
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,0,3,0],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[0], sommets_tetraedre[1])]), 
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,0,0,4],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[1], sommets_tetraedre[2])]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [0,2,0,4],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[2], sommets_tetraedre[3])]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [0,2,3,0],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[3], sommets_tetraedre[0])]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,2,0,0],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[0], sommets_tetraedre[2])]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [0,0,3,4],
                     [(s1+s2)*self.coeff_translation for s1,s2 in zip(sommets_tetraedre[1], sommets_tetraedre[3])]),

            # Tétraèdres des extrémités (translations du tétrèdre de base par chacun des vecteurs sommets); envisager une boucle
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,2,3,0],
                     [2*s*self.coeff_translation for s in sommets_tetraedre[0]]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,0,3,4],
                     [2*s*self.coeff_translation for s in sommets_tetraedre[1]]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [1,2,0,4],
                     [2*s*self.coeff_translation for s in sommets_tetraedre[2]]),
            Polyedre(sommets_tetraedre, aretes_tetraedre, faces_tetraedre, couleurs_aretes_tetraedre, [0,2,3,4],
                     [2*s*self.coeff_translation for s in sommets_tetraedre[3]])

        ]
        # Constructions des 4 octaèdres (translations de l'octaèdre de référence par chacun des vecteurs sommet du tétraèdre de référence)
        # Envisager une boucle
        self.octaedres = [
            Polyedre(sommets_octaedre, aretes_octaedre, faces_octaedre, couleurs_aretes_octaedre, [2,0,3,0,0,0,0,1],
                     sommets_tetraedre[0], -np.arccos(np.sqrt(3)/3), [1,0,0]), 
            Polyedre(sommets_octaedre, aretes_octaedre, faces_octaedre, couleurs_aretes_octaedre, [0,0,3,0,0,4,0,1],
                     sommets_tetraedre[1], -np.arccos(np.sqrt(3)/3), [1,0,0]),
            Polyedre(sommets_octaedre, aretes_octaedre, faces_octaedre, couleurs_aretes_octaedre, [2,0,0,0,0,4,0,1],
                     sommets_tetraedre[2], -np.arccos(np.sqrt(3)/3), [1,0,0]),
            Polyedre(sommets_octaedre, aretes_octaedre, faces_octaedre, couleurs_aretes_octaedre, [2,0,3,0,0,4,0,0],
                     sommets_tetraedre[3], -np.arccos(np.sqrt(3)/3), [1,0,0])
        ]
        for i in range (0,4): self.octaedres[i].translation([(self.coeff_translation-1) * s for s in self.tetraedre_reference.sommets_initiaux[i]])
    # Afficher la pyramide revient à afficher chacun de ses polyèdres
    def afficher(self):
        for octaedre in self.octaedres:
            octaedre.afficher()
        for tetraedre in self.tetraedres:
            tetraedre.afficher()
        self.tetraedre_reference.afficher_axes()
    # Tourner la pyramide revient à tourner chacun de ses polyèdres
    def rotation(self, angle, vecteur):
        for octaedre in self.octaedres:
            octaedre.rotation(angle, vecteur)
        for tetraedre in self.tetraedres:
            tetraedre.rotation(angle, vecteur)

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

    #polyedre='cube' 
    polyedre='tetrahedron' 
    
    if polyedre == "cube" :
        # instanciation du Rubik_cube
        rubik_cube = Rubik_cube(ratio=display[0]/display[1])
        rubik_cube.gerer_affichage_cube(gestion_clavier)
        # pyOpenGl
        gluPerspective(45, rubik_cube.ratio, 0.1, 50.0)
        glTranslatef(0.0,0.0, -30) 
        glEnable(GL_DEPTH_TEST) # Permet de cacher les objets placés derrière d'autres objets
    elif polyedre == "tetrahedron" :
        rubik_tetra = Rubik_tetrahedron(ratio=display[0]/display[1])
        # pyOpenGl
        gluPerspective(45, rubik_tetra.ratio, 0.1, 50.0)
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


