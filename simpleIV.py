#!/usr/bin/python
import pygame, os, random, math
import cProfile

class Image:
    def __init__(self,id, p,x,y,r,m):
        self.path = p

        self.id  = id
        try:
            self.img   = pygame.image.load(p).convert()
            self.thumb = pygame.transform.rotozoom(self.img,0, self.calcMul(128) )
        except pygame.error, message:
            self.thumb = None
            return
        self.img  = self.thumb
        self.limg = None

        self.x    = x
        self.y    = y
        self.rot  = r
        self.mul  = m
        self.size = 0
        self.time = 0

        self.tx   = self.x
        self.ty   = self.y
        self.trot = self.rot
        self.tsize = 0

        self.large = False

    def show(self,scr ):
        self.mul = float(self.size)/float(self.img.get_width())

        if self.mul < 0.01: return
        if abs(self.mul-1.0)<0.04:
            scr.blit( self.img,
                      [self.x-self.img.get_width()*self.mul/2,
                       self.y-self.img.get_height()*self.mul/2])
        else:
            scr.blit(pygame.transform.rotozoom(
                    self.img, self.rot, self.mul),
                     [self.x-self.img.get_width()*self.mul/2,
                      self.y-self.img.get_height()*self.mul/2] )

    def setLarge( self, l = 5 ):
        self.large = l
    def resetLarge( self ):
        self.large = 0

    def loadLarge( self ):
        if self.large == 0 or self.large == 1 or self.limg != None:
            return
        self.large -= 1
        if self.large == 1:
            try:
                self.limg = pygame.image.load(self.path).convert()
                self.img  = self.limg
            except pygame.error, message:
                self.limg = None

    def freeLarge( self ):
        if self.large == 0 and self.limg != None:
            self.limg = None
            self.img = self.thumb
        
    def update(self, scr ):
        if self.time == 0:
            self.time -= 1
            self.x, self.y, self.size = self.tx, self.ty, self.tsize

        elif self.time > 0:
            self.loadLarge()
            self.freeLarge()

            self.time -= 1
            speed = 2

            self.x += (self.tx - self.x )/speed
            self.y += (self.ty - self.y )/speed
            self.size += (self.tsize - self.size)/speed
        self.show( scr )

    def moveToTarget( self ):
        self.x, self.y = self.tx, self.ty

    def setTgtX( self, x, y, r, szX ):
        self.tx,self.ty  = x,y
        self.trot        = r
        self.tsize       = int(szX)
        self.time        = 15

    def setTgtXY( self, x, y, r, sz ):
        if self.img.get_width() > self.img.get_height():
            s2 = sz
        else:
            s2 = int(float(sz)/self.img.get_height()*self.img.get_width())
        self.setTgtX( x, y, r, s2 )

    def setHide( self ):
        self.tsize = 0
        self.time  = 15
    
    def setDtlTgt( self, x, y, r, m, t ):
        pass

    def inPos( self, pos ):
        x0 = pos[0] - self.x + self.img.get_width() *self.mul/2
        y0 = pos[1] - self.y + self.img.get_height()*self.mul/2
        a = - math.pi*self.rot/360
        x1, y1 = x0*math.cos(a)-y0*math.sin(a), x0*math.sin(a)+y0*math.cos(a)
        if (0 < x1 and x1 < self.img.get_width()  * self.mul and
            0 < y1 and y1 < self.img.get_height() * self.mul ) :
            return True
        return False

    def calcMul( self, size ):
        if self.img == None : return 0.0
        if self.img.get_width() > self.img.get_height():
            return float(size)/self.img.get_width()
        else:
            return float(size)/float(self.img.get_height())

class ModeRandom:
    def __init__(self):
        self.size = 64

    def resetPos( self, imgs ):
        for im in imgs.imgs:
            im.setTgtXY( random.random()*imgs.width, random.random()*imgs.height,
                       random.random()*360, self.size )

    def resizeScreen( self, imgs ):
        self.resetPos( imgs )

    def keySpc( self, imgs ):
        self.resetPos( imgs )
    def pageUp( self, imgs  ):
        pass
    def pageDown(self, imgs ):
        pass

class ModeCatalog:
    def __init__(self):
        self.size   = 128
        self.offset = 0

    def setPos( self, imgs, im ):
        w = imgs.width/self.size
        x = self.size/2+ int(im.id%w)*self.size
        y = self.size/2+ int(im.id/w)*self.size+self.offset
        im.setTgtXY( x, y, 0, self.size )
        # im.moveToTarget()

    def resetPos( self, imgs ):
        for im in imgs.imgs:
            self.setPos( imgs, im )

    def setMode( self, imgs ):
        self.resetPos( imgs )

    def resizeScreen( self, imgs ):
        self.resetPos( imgs )

    def setOffset( self, imgs, off ):
        w = imgs.width/self.size
        y = int(off/w)*self.size-imgs.height/2+self.size/2
        self.offset = -y

    def onLClick( self, imgs, id ):
        ModeScroll.setOffset( imgs, id )
        return ModeScroll

    def keySpc( self, imgs ):
        self.resetPos( imgs )

    def pageUp( self, imgs ):
        if self.offset < 0:
            self.offset += self.size
        self.resetPos( imgs )

    def pageDown( self, imgs ):
        self.offset -= self.size
        w = int(imgs.width/self.size)
        ymax = int(len(imgs.imgs)/w)*self.size
        if self.offset < -ymax:
            self.offset = -ymax
        self.resetPos( imgs )

    def update( self, imgs ):
        if self.offset > 0:
            self.offset = int(self.offset / 16.0)
            self.resetPos( imgs )
        w = int(imgs.width/self.size)
        ymax = int(len(imgs.imgs)/w)*self.size
        if self.offset < -ymax:
            self.offset = -ymax

class ModeScroll:
    def __init__(self):
        self.No     = 3
        self.offset = 0

    def setMode( self, imgs ):
        for im in imgs.imgs:
            im.setHide()
            im.resetLarge()
        self.resetPos( imgs )

    def setPos( self, imgs, im ):
        im.setHide()
        im.resetLarge()

    def resetPos( self, imgs ):
        for im in imgs.imgs:
            im.setHide()
            im.resetLarge()

        im = imgs.imgs[self.offset]
        im.setLarge()

        height = imgs.height
        x, y = 0, imgs.height/2
        tw = im.img.get_width() * imgs.height / im.img.get_height() 
        im.setTgtX( imgs.width/2.0, y, 0, tw )
        x1 = imgs.width/2.0 - tw/2.0
        x2 = imgs.width/2.0 + tw/2.0

        n = self.offset -1
        o = self.offset +1
        for i in range(self.No):
            if n < 0: 
                n = len(imgs.imgs)-1
            im = imgs.imgs[n]
            im.setLarge(5+i)

            tw = (im.img.get_width() * imgs.height / im.img.get_height() *
                  (0.9-i*0.1))
            x1 -= int(tw/2.0)
            im.setTgtX( x1, y, 0, tw )
            x1 -= int(tw/2.0)
            n -= 1

            if o >= len(imgs.imgs):
                o = 0
            im = imgs.imgs[o]
            im.setLarge(5+i*2)

            tw = (im.img.get_width() * imgs.height / im.img.get_height() *
                  (0.9-i*0.1))
            x2 += int(tw/2.0)
            im.setTgtX( x2, y, 0, tw )
            x2 += int(tw/2.0)
            o += 1

    def resizeScreen( self, imgs ):
        self.resetPos( imgs )

    def setOffset( self, imgs, off ):
        self.offset = off

    def onLClick( self, imgs, id ):
        if id == self.offset:
            ModeCatalog.setOffset( imgs, id )
            return ModeCatalog
        else:
            self.offset = id
            return self

    def keySpc( self, imgs ):
        self.pageDown( imgs )

    def pageUp( self, imgs ):
        self.offset -= 1
        if self.offset < 0: self.offset = len(imgs.imgs)-1
        self.resetPos( imgs )

    def pageDown( self, imgs ):
        self.offset += 1
        if self.offset > len(imgs.imgs) -1:
            self.offset = 0
        self.resetPos( imgs )

    def update( self, imgs ):
        pass

ModeCatalog = ModeCatalog()
ModeScroll  = ModeScroll()
Modes = [ModeCatalog, ModeScroll ]

class Images():
    def __init__( self, w, h ):
        self.files     = []
        self.imgs      = []
        self.width, self.height = w, h
        self.mode = Modes[0]

        self.path = './'
        self.files = sorted(os.listdir(self.path))

    # Animation
    def update( self, scr ):
        # File Read
        for i in range(8):
            if len(self.files) < 1: break
            id = len(self.imgs)
            im = Image(id, self.path+self.files.pop(), 0,0,0,0 )
            if im.thumb == None: continue

            self.imgs.append( im )
            self.mode.setPos( self, im )
            im.moveToTarget()

            # self.mode.update( self )

        for im in self.imgs:
            im.update( scr )

    # Events
    def onLClick( self, pos ):
        i = len(self.imgs)
        for im in reversed(self.imgs):
            i = i - 1
            if im.inPos( pos ):
                m = self.mode.onLClick( self, i )
                if m != None:
                    self.mode = m
                    self.mode.setMode( self )
                break

    def setMode( self, mode ):
        self.mode = mode
        self.mode.setMode( self )

    def toggleMode( self ):
        # self.mode = self.modes.pop()
        m = Modes.pop()
        Modes.insert(0,m)
        self.setMode( m )
        self.resetPos( )

    def resizeScreen( self, w, h ):
        self.width, self.height = w, h
        self.mode.resizeScreen( self )

    def pageUp( self ):   self.mode.pageUp( self )
    def pageDown(self):   self.mode.pageDown( self )

    def resetPos( self ): self.mode.resetPos( self )
    def keySpace( self ): self.mode.keySpc( self )



# Define some colors
white=[255,255,255]
black=[0,0,0]
 
pygame.init()
screen = pygame.display.set_mode([800, 600],pygame.RESIZABLE)
 
pygame.display.set_caption('Window Name')
 
background = pygame.Surface(screen.get_size())
background.fill(black)
 
clock = pygame.time.Clock()

Imgs = Images( 800, 600 )
Imgs.resetPos()

done = False
ctr = 0
Imgs.update( screen )
while done==False:
    clock.tick(10)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                Imgs.onLClick(event.pos)
            if event.button == 4:
                Imgs.pageUp()
            if event.button == 5:
                Imgs.pageDown()

        if event.type== pygame.VIDEORESIZE:
            screen = pygame.display.set_mode([event.w, event.h],
                                             pygame.RESIZABLE)
            Imgs.resizeScreen( screen.get_width(), screen.get_height() )
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                Imgs.keySpace()
            if event.key == pygame.K_m:
                Imgs.toggleMode()
            if event.key == pygame.K_PAGEUP:
                Imgs.pageUp()
            if event.key == pygame.K_PAGEDOWN:
                Imgs.pageDown()

    screen.fill(black)
    #cProfile.run('Imgs.update( screen )')
    Imgs.update( screen )
    
    pygame.display.flip()
 
pygame.quit ()


