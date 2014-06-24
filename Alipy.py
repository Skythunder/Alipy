from World import *
from Creatures import *
from Tile import *
import pygame as pg
from pygame import Color, Rect, Surface
import random as rng
import sys
from collections import defaultdict

#set up pygame
pg.init()
mainClock = pg.time.Clock()
#setup world
world = World("Alipy",nrows=20,ncols=20)
tile_list=defaultdict(dict)
tw=world.tile_width
th=world.tile_height
ww=world.ncols*tw
wh=world.nrows*th
r_offset=0
c_offset=0
for r in xrange(world.nrows):
    c_offset=0
    for c in xrange(world.ncols):
        tile_list[world.getTile(r,c)]=Rect(c_offset,r_offset,tw,th)
        c_offset+=th
    r_offset+=tw
# set up the window
screen = pg.display.set_mode((ww, wh), 0, 32)
pg.display.set_caption(world.name)
# draw the white background onto the surface
WHITE = (255, 255, 255)
screen.fill(WHITE)
pg.display.update()
ccc=Creature()
ccc.generateGene()
world.tiles[12][6].content=ccc
# run the main loop
while True:
    #process events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    #draw world
    for k in tile_list.keys():
        c = k.content
        if c is None: color = WHITE
        else: color = c.color
        pg.draw.rect(screen, color, tile_list[k], 0)
    pg.display.update()
    
            
