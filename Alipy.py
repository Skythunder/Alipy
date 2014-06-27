from World import *
from Creatures import *
from Tile import *
import pygame as pg
from pygame import Color, Rect, Surface
from pygame.locals import *
import random as rng
import sys
from collections import defaultdict

#set up pygame
pg.init()
mainClock = pg.time.Clock()
fps=10
#setup world
world = World("Alipy",nrows=50,ncols=50)
world.readWorld("world.csv")
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
'''
ccc=Creature(1)
ccc.generateGene()
world.tiles[12][6].content=ccc
ccc.xpos=6
ccc.ypos=12
world.creatures[ccc.creature_id]=ccc
'''
#world.randomPop([6,6,6])
world.readPop("lista.csv")
#print str(ccc)
# run the main loop
print_creatures = False
print_creatures_file = False
stats = False
while True:
    #process events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                fps+=10
            if event.key == K_DOWN:
                fps-=10
                if fps<10:
                    fps=10
            if event.key == ord('p'):
                print_creatures=True
            if event.key == ord('w'):
                print_creatures_file=True
            if event.key == ord('s'):
                stats=True
    #update world
    for k in world.creatures.keys():
        if world.creatures[k]:
            world.act(world.creatures[k])
    #ready statistics
    if print_creatures_file:
        header="id;type;predator;prey;energy;r;g;b;speed;eye_type;eye_range;mut_rate;rep_type;xpos;ypos"
        f=open("creatures.csv","w")
        f.write(header+"\n")
    speed=0
    erange=0
    cnt=0
    aura=0
    tunnel=0
    #draw world
    screen.fill(WHITE)
    for k in tile_list.keys():
        c = k.content
        if c is None: color = WHITE
        else:
            color = c.color
            if c.creature_type==1:
                pg.draw.rect(screen,color,tile_list[k],0)
            elif c.creature_type==2:
                pg.draw.circle(screen,color,tile_list[k].center,
                               world.tile_width/2,0)
            else:
                pg.draw.arc(screen,color,tile_list[k],0,180,4)
            if print_creatures:
                print str(c)
            if print_creatures_file:
                f.write(c.str_csv()+"\n")
            if stats:
                speed+=c.speed
                erange+=c.eye_range
                cnt+=1
                if c.eye_type==0:
                    aura+=1
                else:
                    tunnel+=1
    if print_creatures:
        print_creatures=False
    if print_creatures_file:
        f.close()
        print_creatures_file=False
    if stats:
        print "Statistics:"
        print "Medium speed: "+str(speed/float(cnt))
        print "Medium Eye Range: "+str(erange/float(cnt))
        print "Percentage of Aura Vision: "+str(aura/float(cnt))
        print "Percentage of Tunnel Vision: "+str(tunnel/float(cnt))
        stats=False
                
    pg.display.update()
    mainClock.tick(fps)
    
            
