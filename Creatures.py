import random as rnd

##Defines a few possible food and creature types
MOISTURE=0
HERBIVORE=1
CARNIVORE=2
OMNIVORE=3

##Defines possible reprodution types
ASEXUAL=0
SEXUAL=1

##Defines constants
###VISION: (type,min range,max range)
VISION_AURA=(0,1,3)
VISION_CONE=(1,1,5)
VISION_TUNNEL=(2,1,10)
VISION_TYPE=(0,2)
MAX_SPEED=10

#Defines a Creature object
class Creature:

    ##creature_id: unique id for creature
    ##creature_type: defines the creature's type
    #creature_type=HERBIVORE,food=MOISTURE,reprodution=ASEXUAL,speed=0
    def __init__(self,creature_id=-1,creature_type=0,energy=1000,gene=[],
                 xpos=-1,ypos=-1,color=(0,0,0)):
        self.creature_id=creature_id
        self.creature_type=creature_type
        self.xpos=xpos
        self.ypos=ypos
        self.energy=energy
        self.color=color
        if bool(gene):
            self.parseGene(gene)

    #Converts gene data into creature stats
    def parseGene(self,gene):
        self.color=(gene[0],gene[1],gene[2])
        self.speed=int(gene[4]*(float(MAX_SPEED)/255))
        #FIX WHEN VISION_CONE IS IMPLEMENTED!!
        if gene[5]<255/2:
            self.eye_type=VISION_AURA
        else:
            self.eye_type=VISION_TUNNEL
        er=int(gene[6]*(float(self.eye_type[2])/255))
        if er==0:er=1
        self.eye_range=er
        self.mutation_rate=gene[7]*(0.5/255)
        if gene[8]<255/2:
            self.reprodution_type=ASEXUAL
        else:
            self.reprodution_type=SEXUAL

    #Creates and sets random gene
    def generateGene(self,set_gene=True,parse_gene=True):
        gene=[]
        for x in xrange(9):
            gene.append(rnd.randint(0,255))
        if set_gene:
            self.gene=gene
        if parse_gene:
            self.parseGene(gene)
        return gene

    #Get euclidean distance between two colors
    def colorDistance(self,color):
        r1,g1,b1=self.color
        r2,g2,b2=color
        return ((r1-r2)**2+(g1-g2)**2+(b1-b2)**2)**0.5

    #Returns % of success at eating target creature
    def chance2eat(self,creature):
        d=self.colorDistance(creature.color)
        dmax=441.67295593
        return 1-(d*(1.0/dmax))

    def __str__(self):
        s="Creature: "
        s+= str(self.creature_id)
        s+="\nType: "
        s+= str(self.creature_type)
        s+="\nX: "
        s+= str(self.xpos)
        s+="\nY: "
        s+= str(self.ypos)
        s+="\nEnergy: "
        s+= str(self.energy)
        s+="\nColor: "
        s+= str(self.color)
        s+="\nSpeed:"
        s+= str(self.speed)
        s+="\nEye Type: "
        s+= str(self.eye_type)
        s+="  -  Eye Range: "
        s+= str(self.eye_range)
        s+="\nMutation Rate: "
        s+= str(self.mutation_rate)
        s+="\nReprodution Type: "
        s+= str(self.reprodution_type)
        return s        

