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
    rc=rnd.randint(-25,+25)
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
                 world_type=CIRCULAR,turn_cost=10,move_cost=10,breed_cost=400,
                 hunt_cost=50,feed_reward=100,creatures=defaultdict(dict),
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

    ##reads population from file
    def readPop(self,filename):
        f = open(filename,"r")
        content = f.readlines()
        content=content[1:len(content)]
        for x in content:
            r=x.split(";")
            for i in xrange(len(r)):
                r[i]=int(r[i])
            c = Creature(r[0],r[1],r[2],r[3],r[4],r[5:13],r[13],r[14])
            self.creature_cnt+=1
            self.creatures[r[0]]=c
            t=self.getTile(r[14],r[13])
            t.content=c
        f.close()

    ##reads world from file
    def readWorld(self,filename):
        f = open(filename,"r")
        content = f.readlines()
        content=content[1:len(content)]
        x=content[0]
        r=x.split(";")
        self.name=r[0]
        self.nrows=int(r[1])
        self.ncols=int(r[2])
        self.tile_width=int(r[3])
        self.tile_height=int(r[4])
        self.world_type=int(r[5])
        self.turn_cost=int(r[6])
        self.move_cost=int(r[7])
        self.breed_cost=int(r[8])
        self.hunt_cost=int(r[9])
        self.feed_reward=int(r[10])
        f.close()

    ##generate random population
    def randomPop(self,sizes):
        cnt_type=1
        for s in xrange(len(sizes)):
            for x in xrange(s):
                c= Creature(self.creature_cnt)
                c.creature_type=cnt_type
                c.predator=cnt_type+1
                c.prey=cnt_type-1
                c.generateGene()
                ex=False
                for tr in self.tiles:
                    for tc in tr:
                        if tc.isEmpty():
                            c.xpos=tc.xpos
                            c.ypos=tc.ypos
                            tc.content=c
                            ex=True
                            break
                    if ex:
                        break
                self.creature_cnt+=1
                self.creatures[c.creature_id]=c
            cnt_type+=1

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
        if creature.eye_type==VISION_AURA:
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
        elif creature.eye_type==VISION_TUNNEL:
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
            return -1
        elif r<x:
            a.energy+=self.feed_reward
            if a.energy>MAX_ENERGY:
                a.energy=MAX_ENERGY
            self.killCreature(b)
        return 0

    #creates offspring from asexual creatures in position
    def asexBreed(self,a,yp,xp):
        self.creature_cnt+=1
        offspring = Creature(self.creature_cnt,a.creature_type,
                             a.predator,a.prey,xpos=xp,ypos=yp)
        gene=a.gene[:]
        r = rnd.random()
        if r<a.mutation_rate:
            self.mutation(gene)
        offspring.gene=gene
        offspring.parseGene(gene)
        offspring.energy=int(MAX_ENERGY-(MAX_ENERGY/5))
        t=self.getTile(yp,xp)
        t.content=offspring
        self.creatures[offspring.creature_id]=offspring
        a.energy-=self.breed_cost
        if a.energy<=0:
            self.killCreature(a)

    #breeds two creatures
    def breed(self,a,b,yp,xp):
        self.creature_cnt+=1
        offspring = Creature(self.creature_cnt,a.creature_type,
                             a.predator,a.prey,xpos=xp,ypos=yp)
        gene = self.cross(a.gene,b.gene)
        r = rnd.random()
        if r<max(a.mutation_rate,b.mutation_rate):
            self.mutation(gene)
        offspring.gene=gene
        offspring.parseGene(gene)
        offspring.energy=int(MAX_ENERGY-(MAX_ENERGY/5))
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
                    if cur_tile!=tile:
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

    #Finds closest target in list    
    def searchClosestTarget(self,a,targets):
        d=999999
        res=None
        for c in targets:
            daux=self.euclideanDistance(a.xpos,a.ypos,c.xpos,c.ypos)
            if d>daux:
                d=daux
                res=c
        return c

    #return list of possible mates ordered by distance
    def seekMates(self,a,targets):
        res=[]
        for c in targets:
            enr=float(c.energy)/MAX_ENERGY
            if enr>=0.75:
                d=self.euclideanDistance(a.xpos,a.ypos,c.xpos,c.ypos)
                res.append((d,c))
        res.sort(key=lambda x: x[0])
        return res

    #return list of possible prey ordered by distance
    def seekPrey(self,a,targets):
        res=[]
        for c in targets:
            d=self.euclideanDistance(a.xpos,a.ypos,c.xpos,c.ypos)
            res.append((d,c))
        res.sort(key=lambda x: x[0])
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
        if select is not None:
            a.xpos=t.xpos
            a.ypos=t.ypos
            t1.content=None
            t.content=a
            a.energy-=self.move_cost*d
            if a.energy<=0:
                self.killCreature(a)
                return -1
        return 0

    #makes creature take action
    def act(self,a):
        a.energy-=self.turn_cost
        t=self.getTile(a.ypos,a.xpos)
        if a.energy<=0:
            self.killCreature(a)
            return
        seen=self.look(a)
        
        if a.prey==MOISTURE:
            #a.energy+=int(t.moisture*self.feed_reward)
            a.energy+=self.feed_reward*t.moisture
            #a.energy+=self.turn_cost+1
            if a.energy>MAX_ENERGY:
                a.energy=MAX_ENERGY
        
        enr=float(a.energy)/MAX_ENERGY
        done=False
        ##reproduce
        if enr>0.75 and not done:
            if a.reprodution_type==ASEXUAL:
                en=self.emptyNeighbours(1,t)
                if en:
                    r=rnd.randint(0,len(en)-1)
                    self.asexBreed(a,en[r].ypos,en[r].xpos)
                    done=True
            else:
                mates = self.searchTargets(seen,a.creature_type)
                if mates:
                    cand=self.seekMates(a,mates)
                    if cand:
                        dm,m=cand[0]
                        vr=self.approach(a,m,seen)
                        if vr<0:return
                        done=True
                        d=self.euclideanDistance(a.xpos,a.ypos,
                                                 m.xpos,m.ypos)
                        if d<=2:
                            t2=self.getTile(m.ypos,m.xpos)
                            emp=self.emptyNeighbours(1,t)
                            if not emp:
                                emp=self.emptyNeighbours(1,t2)
                            if emp:
                                r=rnd.randint(0,len(emp)-1)
                                self.breed(a,m,emp[r].ypos,emp[r].xpos)
        ##hunt
        if not done:
            prey = self.searchTargets(seen,a.prey)
            if prey:
                cand=self.seekPrey(a,prey)
                dm,m=cand[0]
                vr=self.approach(a,m,seen)
                if vr<0:return
                done=True
                d=self.euclideanDistance(a.xpos,a.ypos,m.xpos,m.ypos)
                if d<=2:
                    self.eat(a,m)
            else:
                ##run from predator
                predator=self.searchTargets(seen,a.predator)
                if predator:
                    pred=self.searchClosestTarget(a,predator)
                    self.run(a,pred)
                    done=True
        if not done:
            ##move
            poss=self.emptyTiles(a.speed,t,seen)
            if poss:
                r=rnd.randint(0,len(poss)-1)
                tt=poss[r]
                d=self.euclideanDistance(a.xpos,a.ypos,tt.xpos,tt.ypos)
                t.content=None
                tt.content=a
                a.xpos=tt.xpos
                a.ypos=tt.ypos
                done=True
                a.energy-=int(d)*self.move_cost
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
    world.creature_cnt=2
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
    print str(c2)
    print world.creatures
    #c.predator=c2.creature_type
    c.energy=300
    world.act(c)
    print world.creatures
    for k in world.creatures.keys():
        print str(world.creatures[k])
