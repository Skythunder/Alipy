###DIRECTION
UP=(-1,0)
DOWN=(1,0)
LEFT=(0,-1)
RIGHT=(0,1)
UPLEFT=(-1,-1)
DOWNLEFT=(1,-1)
UPRIGHT=(-1,1)
DOWNRIGHT=(1,1)

def minDistance(xi,yi,xf,yf):
    if abs(xi-xf)>abs(yi-yf):
        return abs(yi-yf)
    else:
        return abs(xi-xf)

def move(self,direction,speed,yi,xi,nrows,ncols):
    yf=direction[0]*speed + yi
    xf=direction[1]*speed + xi
    if speed < min(nrows,ncols):
        if xf<0:
            #xf=0
            xf=(ncols-1)-(0-xf)
        elif xf >= ncols:
            #xf=ncols-1
            xf=0+(xf-(ncols-1))
        if yf<0:
            #yf=0
            yf=(nrows-1)-(0-yf)
        elif yf >= nrows:
            #yf=nrows-1
            yf=0+(yf-(nrows-1))
    return (yf,xf)

print move(DOWNLEFT,19,2,2,20,20)
