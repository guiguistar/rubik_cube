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
    
if __name__=='__main__':

    print "test block needed"


