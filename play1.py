# Player 1 Program

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import sys, os, pygame, math, random
from pygame.locals import *
from twisted.internet.task import LoopingCall

# Loads images
def load_image(name):
    image = pygame.image.load(name)
    return image, image.get_rect()

# GAMESPACE
class GameSpace():
    def __init__(self, p1Con, reactor):
	# Add network connection
    	self.p1Con = p1Con
        self.reactor = reactor

	# Initialize window settings
	pygame.init()
	pygame.key.set_repeat(100, 30)
        pygame.display.set_caption('kNockDown: player1')
	self.back = 255, 255, 255 
	self.size = self.width, self.height = 640, 480
	self.screen = pygame.display.set_mode(self.size)
		
	# Initialize game objects
	self.clock = pygame.time.Clock()
	self.background = Background(self)
	self.myAvatar = Avatar(self, 'images/squirrelP1.png', 'images/scores/player1_0.png', 10, 330, 0, 0, 1) #1 indicates ownership
        self.enemyAvatar = Avatar(self, 'images/squirrelP2.png', 'images/scores/player2_0.png', 500, 330, 525, 0, 0)
	self.sprites = [self.enemyAvatar, self.myAvatar] # contains list of objects
        self.target = Target(self)
        self.acorns = []

        # Score and Target stuff
        self.score = 0
        random.seed() #seed random number generator from current time

        # start event "loop"
        self.reactor.callLater(1/60, self.loop)
		
    def loop(self):
	for event in pygame.event.get():
	    if event.type == QUIT:
#                self.p1Con.transport.write('quit=1\r\n')
		pygame.quit()
	        os._exit(0)
	    if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.myAvatar.move(self.myAvatar.rect.x - 30) #move left
#   Not sure if we want to do the write here or in tick (where it is now)
#       it doesn't need to happen more often than here, but in the spirit of
#       the clock-tick paradigm, it might be better to leave it in tick?
#                    myPos = 'enemy='+str(self.myAvatar.rect.x)
#                    self.p1Con.transport.write(myPos)
                elif event.key == pygame.K_RIGHT:
                    self.myAvatar.move(self.myAvatar.rect.x + 30) #move right
#                    myPos = 'enemy='+str(self.myAvatar.rect.x)
#                    self.p1Con.transport.write(myPos)
                elif event.key == pygame.K_SPACE:
                    #fire
                    x = self.myAvatar.rect.centerx
                    y = self.myAvatar.rect.y
                    new_acorn = Acorn(self, 'images/acornP1.png', x, y, 1) #1 indicates ownership
                    self.acorns.append(new_acorn)
                    #write data to player 2
                    self.p1Con.transport.write('acorn=\r\n')

	for sprite in self.sprites:
	    sprite.tick()
            sprite.scorecard.tick()
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
            self.screen.blit(i.scorecard.image, i.scorecard.rect)
        for acorn in self.acorns:
            if not acorn.hit:
                self.screen.blit(acorn.image, acorn.rect)
	pygame.display.flip()

        self.reactor.callLater(1/60, self.loop)
		
# BACKGROUND
class Background(pygame.sprite.Sprite):
    def __init__(self, gs):
        self.gs = gs
	pygame.sprite.Sprite.__init__(self)
	self.image, self.rect = load_image('images/booth.jpg')
	self.rect.topleft = 0, 0
    def tick(self):
	pass

# AVATAR CLASS
class Avatar(pygame.sprite.Sprite):
    def __init__(self, gs, image, scoreimage, x, y, scorex, scorey, owner):
        self.gs = gs
	pygame.sprite.Sprite.__init__(self)
	self.image, self.rect = load_image(image)
	self.rect.topleft = x, y
        self.ownership = owner
        self.score = 0
        self.scorecard = Score(self, scoreimage, scorex, scorey)

    def move(self, xpos):
        self.rect.x = xpos
        pygame.display.update(self.rect)

    def tick(self):
        if self.ownership:
            myPos = 'enemy='+str(self.rect.x)+'\r\n' # y position constant
            self.gs.p1Con.transport.write(myPos)

# SCORE CLASS
class Score(pygame.sprite.Sprite):
    def __init__(self, avatar, image, x, y):
        self.avatar = avatar
        pygame.sprite.Sprite.__init__(self)
        self.imagebase = image.split('_')[0]
        self.image, self.rect = load_image(image)
        self.rect.topleft = x, y
        self.score = 0

    def tick(self):
        if self.score != self.avatar.score:
            self.score = self.avatar.score #update score
            newimage = self.imagebase + '_'+str(self.score)+'.png'
            self.image = pygame.image.load(newimage)

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
        self.rect.y = self.rect.y - 40 
        if self.rect.colliderect(self.gs.target.rect) and self.hit == 0 and self.gs.target.show and not self.gs.target.beenHit:
#            print 'P1 score: '+str(self.gs.score)
            self.hit = 1
            #update image to indicate hit target, and which player hit it
            if self.ownership:
                self.gs.target.image = pygame.image.load('images/hitP1.png')
                self.gs.myAvatar.score = self.gs.myAvatar.score + 1
            else:
                self.gs.target.image = pygame.image.load('images/hitP2.png')
                self.gs.myAvatar.score = self.gs.myAvatar.score + 1
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
        self.timePassed = self.timePassed + 1
        self.gs.p1Con.transport.write('targetTime='+str(self.timePassed)+'\r\n')
#        print 'timePassed = '+str(self.timePassed)
        if not self.show and self.timePassed >= 15: #wait .25 second between hit and new target
            self.pos = random.randint(75,465) #new position somewhere inside the booth
            #write new position to player 2
            self.gs.p1Con.transport.write('targetPos='+str(self.pos)+'\r\n')
            #update self
            self.move(self.pos) 
            self.beenHit = 0 #allow target hits to register
            self.doshow()
        elif self.show and self.timePassed == 0:
            self.unshow() #unshow after target hit
            self.image = pygame.image.load('images/leprechaun.png') #reload leprechaun
            

# PLAYER CONNECTION
class PlayerConnection(Protocol):
    def connectionMade(self):
	# Create player connection
	self.game = GameSpace(p1Con.getConnection(), reactor)
#	print("player 1 connection made")
	
    def dataReceived(self, data):
	# server.py has sent data to player 2: update game
#    	print 'data received from player2: ', data
        parts = data.split('=') # get label and value
        pos = parts[1].split('\r') #isolate number
        if parts[0] == 'enemy':
            self.game.enemyAvatar.move(int(pos[0]))
        elif parts[0] == 'acorn':
            x = self.game.enemyAvatar.rect.centerx
            y = self.game.enemyAvatar.rect.y
            new_acorn = Acorn(self.game, 'images/acornP2.png', x, y, 0) #not owned by myAvatar
            self.game.acorns.append(new_acorn)
#            elif parts[0] == 'quit':
#                self.game.pygame.quit()
#                os._exit(0)
		

class PlayerConnectionFactory(Factory):
    def __init__(self):
	self.p1Con = PlayerConnection()
	
    def getConnection(self):
	return self.p1Con

    def buildProtocol(self, addr):
	return self.p1Con


if __name__ == '__main__':
    p1Con = PlayerConnectionFactory()
    reactor.listenTCP(40403, p1Con)
    reactor.run()


