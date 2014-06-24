#Defines a tile object
class Tile:
    
    ##Possible tile types
    NORMAL = 0
    WATER = 1
    FERTILE = 2
    HOT = 3
    COLD = 4
    ##

    ##Parameters:
    ###tile_id: unique id for tile
    ###xpos: position of tile in the x axis
    ###ypos: position of tile in the y axis
    ###tile_type: one of the possible tile types
    ###content: creature currently in tile
    ###moisture: amount of moisture in tile
    def __init__(self,tile_id=-1,xpos=-1,ypos=-1,tile_type=NORMAL,moisture=10,content=None):
        self.tile_id=tile_id
        self.xpos=xpos
        self.ypos=ypos
        self.tile_type=tile_type
        self.content = content
        self.moisture=moisture

    #Check if tile is empty
    def isEmpty(self):
        if self.content is None:
            return True
        return False

    #Get direction to tile
    def orientate(self,tile):
        if self.xpos<tile.xpos:
            x=1
        elif self.xpos==tile.xpos:
            x=0
        else:
            x=-1
        if self.ypos<tile.ypos:
            y=1
        elif self.ypos==tile.ypos:
            y=0
        else:
            y=-1
        return (y,x)
    
    #Return string representation of Tile object
    def __str__(self):
        s=""
        s+= str(self.tile_id)
        return s        
    
