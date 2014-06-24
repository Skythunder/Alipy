from Tile import *
from Creatures import *
import random as rnd
from collections import defaultdict

##WORLD TYPES
TRUNCATED=0
CIRCULAR=1

###DIRECTION
UP=(-1,0)
DOWN=(1,0)
LEFT=(0,-1)
RIGHT=(0,1)
UPLEFT=(-1,-1)
DOWNLEFT=(1,-1)
UPRIGHT=(-1,1)
DOWNRIGHT=(1,1)

##Other variables
MAX_ENERGY=1000

#standard fallout mutation
def mutate(gene):
    ri=rnd.randint(3,len(gene)-1)
    rx=rnd.randint(0,255)
    ri2=rnd.randint(0,2)
    rc=rnd.randint(-20,+20)
    gene[ri]=rx
    if gene[ri2]+rc<0:
        gene[ri2]=0
    elif gene[ri2]+rc>255:
        gene[ri2]=255
    else:
        gene[ri2]+=rc
#standard fallout crossover
def crossover(gene1,gene2):
    ri=rnd.randint(0,len(gene1)-1)
    res1=gene1[:ri]+gene2[ri:]
    res2=gene2[:ri]+gene1[ri:]
    rz=rnd.randint(0,1)
    if rz:
        return res1
    else:
        return res2

#Defines the world properties
class World:

    ##Parameters:
    ###name: world name
    ###nrows: number of tiles per row
    ###ncols: number of tiles per column
    ###tile_width: tile width in pixels
    ###tile_height: tile heigth in pixels
    ###world_type: if it loops around edges or not: CIRCULAR vs TRUNCATED
    ###turn_cost:energy cost per turn
    ###move_cost:cost per speed unit
    ###breed_cost: cost to reproduce
    ###hunt_cost: cost to hunt
    ###feed_reward: how much energy a creature gains for eating
    ###creatures: dictionary of all creatures in world
    ###mutation: function for gene mutation
    ###cross: function for crossover
    ##Also contains:
    ###tiles: matrix nrows*nclos containing all tiles
    ###creature_cnt: counter for creatures
    def __init__(self,name,nrows=20,ncols=20,tile_width=10,tile_height=10,
                 world_type=CIRCULAR,turn_cost=10,move_cost=10,breed_cost=50,
                 hunt_cost=20,feed_reward=60,creatures=defaultdict(dict),
                 mutation=mutate,cross=crossover):
        self.name=name
        self.nrows=nrows
        self.ncols=ncols
        self.tile_width=tile_width
        self.tile_height=tile_height
        self.world_type=world_type
        self.turn_cost=turn_cost
        self.move_cost=move_cost
        self.breed_cost=breed_cost
        self.hunt_cost=hunt_cost
        self.feed_reward=feed_reward
        self.creatures=creatures
        self.mutation=mutation
        self.cross=crossover
        self.tiles=[]
        self.creature_cnt=len(creatures)
        t_id=0
        for r in xrange(nrows):
            self.tiles.append([])
            for c in xrange(ncols):
                self.tiles[r].append(Tile(tile_id=t_id,xpos=c,ypos=r))
                t_id+=1

    def move(self,creature,direction,speed):
        xi=creature.xpos
        yi=creature.ypos
        yf=direction[0]*speed + yi
        xf=direction[1]*speed + xi
        if self.world_type == CIRCULAR:
            if xf<0:
                #xf=0
                xf=(self.ncols-1)-(0-xf)
            elif xf >= self.ncols:
                #xf=self.ncols-1
                xf=0+(xf-(self.ncols-1))
            if yf<0:
                #yf=0
                yf=(self.nrows-1)-(0-yf)
            elif yf >= self.nrows:
                #yf=self.nrows-1
                yf=0+(yf-(self.nrows-1))
        elif world_type == TRUNCATED:
            if xf<0:
                xf=0
            elif xf >= self.ncols:
                xf=self.ncols-1
            if yf<0:
                yf=0
            elif yf >= self.nrows:
                yf=self.nrows-1
        go_to=self.tiles[yf][xf]
        cur_tile=self.tiles[creature.ypos][creature.xpos]
        if go_to.content is None:
            cur_tile.content=None
            go_to.content=creature
            creature.xpos=xf
            creature.ypos=yf
        else:
            raise Exception('Tile already occupied!\n')

    def look(self,creature,at=None):
        visible=[]
        xi=creature.xpos
        yi=creature.ypos
        if creature.eye_type==VISION_AURA[0]:
            er = creature.eye_range
            #er=int(er/2)
            for r in xrange(-er,er+1):
                tr=r+yi
                for c in xrange(-er,er+1):
                    tc=c+xi
                    if self.world_type == CIRCULAR:
                        if tc>=self.ncols:
                            tc=0+(tc-(self.ncols-1))
                        if tr>=self.nrows:
                            tr=0+(tr-(self.nrows-1))
                    elif self.world_type == TRUNCATED:
                        if tc>=self.ncols:
                            tc=self.ncols-1
                        if tr>=self.nrows:
                            tr=self.nrows-1
                    if tr==yi and tc==xi:
                        continue
                    visible.append(self.getTile(tr,tc))
        elif creature.eye_type==VISION_TUNNEL[0]:
            if at is None:
                lx=rnd.randint(-1,1)
                ly=rnd.randint(-1,1)
            else:
                ly=at[0]
                lx=at[1]
            for x in xrange(creature.eye_range):
                visible.append(self.getTile(ly*x,lx*x))
        #VISION_CONE MISSING
        return visible

    #creature a consumes creature b - FUTURE: Combat
    def eat(self,a,b):
        x=a.chance2eat(b)
        r=rnd.random()
        a.energy-=self.hunt_cost
        if a.energy<=0:
            self.killCreature(a)
        elif r<x:
            a.energy+=self.feed_reward
            if a.energy>MAX_ENERGY:
                a.energy=MAX_ENERGY
        self.killCreature(b)

    #creates offspring from asexual creatures in position
    def asexBreed(self,a,yp,xp):
        self.creature_cnt+=1
        offspring = Creature(self.creature_cnt,a.creature_type,xpos=xp,ypos=yp)
        gene=a.gene[:]
        r = rnd.random()
        if r<a.mutation_rate:
            self.mutation(gene)
        offspring.gene=gene
        offspring.parseGene(gene)
        t=self.getTile(yp,xp)
        t.content=offspring
        self.creatures[offspring.creature_id]=offspring
        a.energy-=self.breed_cost
        if a.energy<=0:
            self.killCreature(a)

    #breeds two creatures
    def breed(self,a,b,yp,xp):
        self.creature_cnt+=1
        offspring = Creature(self.creature_cnt,a.creature_type,xpos=xp,ypos=yp)
        gene = self.cross(a.gene,b.gene)
        r = rnd.random()
        if r<max(a.mutation_rate,b.mutation_rate):
            self.mutation(gene)
        offspring.gene=gene
        offspring.parseGene(gene)
        t=self.getTile(yp,xp)
        t.content=offspring
        self.creatures[offspring.creature_id]=offspring
        a.energy-=self.breed_cost
        if a.energy<=0:
            self.killCreature(a)
        b.energy-=self.breed_cost
        if b.energy<=0:
            self.killCreature(b)

    #kills creature
    def killCreature(self,a):
        t=self.getTile(a.ypos,a.xpos)
        t.content=None
        del(self.creatures[a.creature_id])

    #Get minimum distance between two tiles -- Not working as intended
    def minDistance(self,xi,yi,xf,yf):
        if abs(xi-xf)>abs(yi-yf):
            return abs(yi-yf)
        else:
            return abs(xi-xf)

    #Get Euclidean distance between two tiles
    def euclideanDistance(self,xi,yi,xf,yf):
        return int(((xi-xf)**2+(yi-yf)**2)**0.5)

    #Check if tile has neighbours of a certain type
    def neighbours(self,creature_type,tile):
        for y in xrange(-1,2):
            for x in xrange(-1,2):
                ty=tile.ypos+y
                tx=tile.xpos+x
                if self.world_type == CIRCULAR:
                    if tx>=self.ncols:
                        tx=0+(tx-(self.ncols-1))
                    if ty>=self.nrows:
                        ty=0+(ty-(self.nrows-1))
                elif self.world_type == TRUNCATED:
                    if tx>=self.ncols:
                        tx=self.ncols-1
                    if ty>=self.nrows:
                        ty=self.nrows-1
                tc=self.getTile(ty,tx).content
                if tc is not None:
                    if tc.creature_type == creature_type:
                        return True
        return False

    #returns list of empty tiles in neighbourhood
    def emptyNeighbours(self,move_range,tile):
        l=[]
        for r in xrange(-move_range,move_range+1):
            for c in xrange(-move_range,move_range+1):
                tr=tile.ypos+r
                tc=tile.xpos+c
                if self.world_type == CIRCULAR:
                    if tc>=self.ncols:
                        tc=0+(tc-(self.ncols-1))
                    if tr>=self.nrows:
                        tr=0+(tr-(self.nrows-1))
                elif self.world_type == TRUNCATED:
                    if tc>=self.ncols:
                        tc=self.ncols-1
                    if tr>=self.nrows:
                        tr=self.nrows-1
                if tr==tile.ypos and tc==tile.xpos:
                    continue
                tt=self.getTile(tr,tc)
                if tt.isEmpty():
                    l.append(tt)
        return l

    #returns list of empty tiles in list within range
    def emptyTiles(self,move_range,cur_tile,tiles):
        res=[]
        for tile in tiles:
            if tile.isEmpty():
                d=self.euclideanDistance(tile.xpos,tile.ypos,
                                   cur_tile.xpos,cur_tile.ypos)
                if d<=move_range:
                    res.append(tile)
        return res

    #checks list of tiles for targets
    def searchTargets(self,tiles,target_type):
        res=[]
        for tile in tiles:
            c=tile.content
            if c is not None:
                if c.creature_type==target_type:
                    res.append(c)
        return res

    #makes creature run away from target -- SLOW?
    def run(self,a,b):
        t1=self.getTile(a.ypos,a.xpos)
        t2=self.getTile(b.ypos,b.xpos)
        y,x=t1.orientate(t2)
        y=-y
        x=-x
        seen=self.look(a,(y,x))
        empty=self.emptyTiles(a.speed,t1,seen)
        if empty:
            cand=[]
            for tile in empty:
                if not self.neighbours(a.speed,tile):
                    cand.append(tile)
            if cand:
                r=rnd.randint(0,len(cand)-1)
                new_pos=cand[r]
                t1.content=None
                new_pos.content=a
                a.xpos=new_pos.xpos
                a.ypos=new_pos.ypos
                d=self.euclideanDistance(t1.xpos,t1.ypos,a.xpos,a.ypos)
                a.energy-=self.move_cost*d
                if a.energy<=0:
                    self.killCreature(a)

    #move creature towards target -- SLOW?
    def approach(self,a,b,seen):
        t1=self.getTile(a.ypos,a.xpos)
        t2=self.getTile(b.ypos,b.xpos)
        y,x=t1.orientate(t2)
        empty=self.emptyTiles(a.speed,t1,seen)
        d=9999999
        select=None
        for t in empty:
            daux=self.euclideanDistance(a.xpos,a.ypos,t.xpos,t.ypos)
            if d>daux:
                d=daux
                select=t
        print d
        print daux
        if select is not None:
            a.xpos=t.xpos
            a.ypos=t.ypos
            t1.content=None
            t.content=a
            a.energy-=self.move_cost*d
            if a.energy<=0:
                self.killCreature(a)

    #Access world position
    def getTile(self,r,c):
        return self.tiles[r][c]
    
    #Returns string representation of World
    def __str__(self):
        s=""
        s+= "World:"+self.name+"\n"
        s+= "Rows: "+str(self.nrows)+"\n"
        s+= "Columns: "+str(self.ncols)+"\n"
        s+= "Tile size:" +str(self.tile_width)+"x"+str(self.tile_height)+"\n"
        for r in xrange(self.nrows):
            s+="\n"
            for c in xrange(self.ncols):
                s+= str(self.tiles[r][c])+" "
        s+="\n"
        return s

if __name__=="__main__":
    world = World("Novo Mundo")
    print str(world)
    c = Creature(creature_id=0,creature_type=1)
    c2 = Creature(creature_id=1,creature_type=2)
    c.generateGene()
    c2.generateGene()
    print str(c)
    world.mutation(c.gene)
    c.parseGene(c.gene)
    print str(c)
    print str(c2)
    c.xpos=0
    c.ypos=0
    c2.xpos=1
    c2.ypos=1
    world.tiles[0][0].content=c
    world.tiles[1][1].content=c2
    #world.move(c,DOWNRIGHT,4)
    #print world.getTile(4,4).content.creature_id
    print world.getTile(0,0).tile_id
    #world.move(c2,DOWNRIGHT,3)
    c.eye_type=VISION_AURA[0]
    c.eye_range=1
    seen = world.look(c)
    '''
    red=(0,0,0)
    blue=(255,0,0)
    c.color=red
    c2.color=blue
    '''
    print c.chance2eat(c2)
    #print world.neighbours(1,world.getTile(0,19))
    #print world.emptyNeighbours(1,world.getTile(3,19))
    t1=world.tiles[0][0]
    t2=world.tiles[1][0]
    print t2.orientate(t2)
    #print world.emptyTiles(3,t1,seen)
    world.creatures[c.creature_id]=c
    world.creatures[c2.creature_id]=c2
    #world.eat(c,c2)
    #print str(world.creatures[c.creature_id])
    #print str(world.creatures[c2.creature_id])
    print c.gene
    print c2.gene
    world.breed(c,c2,0,1)
    o=world.getTile(0,1).content
    print o.gene
    print seen
    print world.searchTargets(seen,1)
    print str(c)
    world.run(c,c2)
    print str(c)
    seen = world.look(c)
    world.approach(c,c2,seen)
    print str(c)
