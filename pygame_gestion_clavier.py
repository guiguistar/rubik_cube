#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Gestion_clavier():


    map_keys={}
    map_keys['a']=pygame.K_a
    map_keys['c']=pygame.K_c
    map_keys['d']=pygame.K_d
    map_keys['e']=pygame.K_e
    map_keys['f']=pygame.K_f
    map_keys['q']=pygame.K_q
    map_keys['r']=pygame.K_r
    map_keys['s']=pygame.K_s
    map_keys['t']=pygame.K_t
    map_keys['x']=pygame.K_x
    map_keys['y']=pygame.K_y



    def __init__(self):

        self.fleche_gauche = False
        self.fleche_droite = False
        self.fleche_haut = False
        self.fleche_bas = False
        self.touche_p = False
        self.touche_m = False
        self.keys=[]

    def check_event_key(self,event):

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
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:  self.fleche_gauche = False
            if event.key == pygame.K_RIGHT: self.fleche_droite = False
            if event.key == pygame.K_UP:    self.fleche_haut = False
            if event.key == pygame.K_DOWN:  self.fleche_bas = False
            if event.key == pygame.K_p:     self.touche_p = False
            if event.key == pygame.K_m:     self.touche_m = False
        
        if event.type == pygame.KEYDOWN:
            for key in self.keys:
#                print key
                if event.key == self.map_keys[key[0]] : key[1](key[2])  


    def add_key(self,key,fonction,args):
        self.keys.append([key,fonction,args])
#        print self.keys[-1]

def fonction_e(args):
    print len(args)
    print "in fonction_e"
def fonction_f(args):
    print len(args)
    print "in fonction_f"
def fonction_quit(args):
    pygame.quit()
    quit()

if __name__=="__main__":

    # pygame
    pygame.init()
    display = (600,600)
    infopygame = pygame.display.Info()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (infopygame.current_w,infopygame.current_h)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    camera=Gestion_clavier()

    camera.add_key("e",fonction_e,['arg1','arg2'])
    camera.add_key("f",fonction_f,[])
    camera.add_key("q",fonction_quit,[])

    while True:
        
        for event in pygame.event.get(): camera.check_event_key(event)

        if camera.fleche_gauche: print "fleche gauche"
        if camera.fleche_droite: print "fleche droite" 
        if camera.fleche_haut:   print "fleche haut" 
        if camera.fleche_bas:    print "fleche bas" 
        if camera.touche_p:      print "touche p" 
        if camera.touche_m:      print "touche m" 

