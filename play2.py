# Player 2 Program

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import sys, os, pygame, math
from pygame.locals import *
from twisted.internet.task import LoopingCall


# Function that loads images
def load_image(name):
    image = pygame.image.load(name)
    image = image.convert()
    return image, image.get_rect()

# GAMESPACE
class GameSpace():
    def __init__(self, p2Con, reactor):
	# Add network connection
	self.p2Con = p2Con
        self.reactor = reactor

	# Initialize window settings
	pygame.init()
	pygame.key.set_repeat(100, 30)
        pygame.display.set_caption('kNockDown: player2')
	self.back = 30, 144, 255
	self.size = self.width, self.height = 640, 480
	self.screen = pygame.display.set_mode(self.size)

	# Initialize game objects
	self.clock = pygame.time.Clock()
	self.background = Background(self)
	self.myAvatar = Avatar(self, 'images/squirrelP2.png', 500, 330, 1) #1 for ownership
        self.enemyAvatar = Avatar(self, 'images/squirrelP1.png', 10, 330, 0)
	self.sprites = [self.enemyAvatar, self.myAvatar]
        self.target = Target(self)
        self.acorns = []

        # Score and Target stuff
        self.score = 0
#        random.seed() #seed random number generator from current time
#   P1 is in charge of setting and communicating the target position

        # start game "loop"
        self.reactor.callLater(1/60, self.loop)

    def loop(self):
	for event in pygame.event.get():
	    if event.type == QUIT:
		pygame.quit()
		os._exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.myAvatar.move(self.myAvatar.rect.x - 30) #move left
                elif event.key == pygame.K_RIGHT:
                    self.myAvatar.move(self.myAvatar.rect.x + 30) #move right
                elif event.key == pygame.K_SPACE:
                    #fire
                    x = self.myAvatar.rect.centerx
                    y = self.myAvatar.rect.y
                    new_acorn = Acorn(self, 'images/acornP2.png', x, y, 1) # 1 indicates ownership
                    self.acorns.append(new_acorn)
                    #write data to player 1
                    self.p2Con.transport.write('acorn=\r\n')

        for sprite in self.sprites:
            sprite.tick()
        for acorn in self.acorns:
            if acorn.hit: 
                self.acorns.remove(acorn) #delete acorn
            else:
                acorn.tick()
        self.target.tick()

	# Update screen
	self.screen.fill(self.back)
        self.screen.blit(self.background.image, self.background.rect)
        if self.target.show:
            self.screen.blit(self.target.image, self.target.rect)
	for i in self.sprites:
	    self.screen.blit(i.image, i.rect)
        for acorn in self.acorns:
            if not acorn.hit:
                self.screen.blit(acorn.image, acorn.rect)
	pygame.display.flip()

        self.reactor.callLater(1/60, self.loop)

# BACKGROUND
class Background(pygame.sprite.Sprite):
    def __init__(self, gs):
	pygame.sprite.Sprite.__init__(self)
	self.image, self.rect = load_image('images/booth.jpg') 
	self.rect.topleft = 0, 0
    def tick(self):
	pass

# AVATAR CLASS
class Avatar(pygame.sprite.Sprite):
    def __init__(self, gs, image, x, y, owner):
        self.gs = gs
	pygame.sprite.Sprite.__init__(self)
	self.image, self.rect = load_image(image)
	self.rect.topleft = x, y
        self.ownership = owner

    def move(self, xpos):
        self.rect.x = xpos
        pygame.display.update(self.rect)

    def tick(self):
        if self.ownership:
            myPos = 'enemy='+str(self.rect.x)+'\r\n' # y position constant
            self.gs.p2Con.transport.write(myPos)

# ACORN CLASS
class Acorn(pygame.sprite.Sprite):
    def __init__(self, gs, image, x, y, owner):
        self.gs = gs
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image)
        self.rect.topleft = x, y
        self.ownership = owner
        self.hit = 0

    def tick(self):
        self.rect.y = self.rect.y - 60
        if self.rect.colliderect(self.gs.target.rect) and self.hit == 0 and self.gs.target.show and not self.gs.target.beenHit:
            self.gs.score = self.gs.score + 1
            self.hit = 1
            #update image to indicate hit target and which player hit it
            if self.ownership:
                self.gs.target.image = pygame.image.load('images/hitP2.png')
            else:
                self.gs.target.image = pygame.image.load('images/hitP1.png')
            #set "timer" before target disappears
            self.gs.target.timePassed = -5
            self.gs.target.beenHit = 1

# TARGET CLASS
class Target(pygame.sprite.Sprite):
    def __init__(self, gs):
        self.gs = gs
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('images/leprechaun.png')
        self.rect.topleft = 340, 200
        self.show = 0 #initially invisible
        self.beenHit = 1 #initially cannot be hit (b/c invisible), so register as already hit
        self.timePassed = 0
        self.pos = 0

    def move(self, x):
        self.rect.x = x

    def doshow(self):
        if not self.show:
            self.show = 1
        else:
            pass

    def unshow(self):
        if self.show:
            self.show = 0
        else:
            pass

    def tick(self):
        print 'self.show = '+str(self.show)
        print 'self.timePassed = '+str(self.timePassed)
        #don't update target position/timePassed, because that is synced from P1 via a write
        if not self.show and self.timePassed >= 15:
            self.move(self.pos)
            self.beenHit = 0 #allow target hits to register
            self.doshow()
        elif self.show and self.timePassed == 0:
            self.unshow() #unshow after target hit
            self.image = pygame.image.load('images/leprechaun.png')


# PLAYER 2 CONNECTION
class PlayerConnection(Protocol):
    def connectionMade(self):
	# Create player connection
	print'player 2 connection made'
	self.game = GameSpace(p2Con.getConnection(),reactor)

    def dataReceived(self, data):
	# server.py has sent data to player 1: update game
	print 'data received from player1: ', data
        parts = data.split('=') #get label and value
        pos = parts[1].split('\r') #isolate number
        print pos
        next_data = pos[1].split('\n')
        print next_data
        if parts[0] == 'enemy':
            self.game.enemyAvatar.move(int(pos[0]))
        elif parts[0] == 'acorn':
            x = self.game.enemyAvatar.rect.centerx
            y = self.game.enemyAvatar.rect.y
            new_acorn = Acorn(self.game, 'images/acornP1.png', x, y, 0) #not owned by myAvatar
            self.game.acorns.append(new_acorn)
# The issue here is that the enemy data and target data is getting sent basically at the same time,
#   so it's all in one data string.  I need to change how I am parsing it
# I think this will also sometimes be a problem with the acorn and targetPos data--though I'm not
#   sure why it wasn't a problem with the acorn
        elif parts[0] == 'targetTime':
            print 'targetTime: '+pos[0]
            self.game.target.timePassed = int(pos[0])
        elif parts[0] == 'targetPos':
            self.game.target.pos = int(pos[0])


class PlayerConnectionFactory(ClientFactory):
    def __init__(self):
	self.p2Con = PlayerConnection()
	
    def getConnection(self):
	return self.p2Con

    def buildProtocol(self, addr):
	return self.p2Con


if __name__ == "__main__":
    p2Con = PlayerConnectionFactory()
    reactor.connectTCP("ash.campus.nd.edu", 40403, p2Con)
    reactor.run()

