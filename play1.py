# Player 1 Program

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import sys, os, pygame, math
from pygame.locals import *
from twisted.internet.task import LoopingCall

# Loads images
def load_image(name):
    image = pygame.image.load(name)
    image = image.convert()
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
	self.myAvatar = Avatar(self, 'images/globe.png', 10, 20, 1) #1 indicates ownership
        self.enemyAvatar = Avatar(self, 'images/greensquare.png', 10, 10, 0)
	self.sprites = [self.enemyAvatar, self.myAvatar] # contains list of objects
	self.allsprites = pygame.sprite.RenderPlain(self.sprites)

        # start event "loop"
        self.reactor.callLater(1/60, self.loop)
		
    def loop(self):
	for event in pygame.event.get():
	    if event.type == QUIT:
		pygame.quit()
	        os._exit(0)
	    if event.type == KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.myAvatar.move(self.myAvatar.rect.x - 5) #move left
#   Not sure if we want to do the write here or in tick (where it is now)
#       it doesn't need to happen more often than here, but in the spirit of
#       the clock-tick paradigm, it might be better to leave it in tick?
#                    myPos = 'enemy='+str(self.myAvatar.rect.x)
#                    self.p1Con.transport.write(myPos)
                elif event.key == pygame.K_RIGHT:
                    self.myAvatar.move(self.myAvatar.rect.x + 5) #move right
#                    myPos = 'enemy='+str(self.myAvatar.rect.x)
#                    self.p1Con.transport.write(myPos)
#                elif event.key == pygame.K_SPACE:
                    #fire
	for sprite in self.sprites:
	    sprite.tick()

	# Update screen
	self.screen.fill(self.back)
        self.screen.blit(self.background.image, self.background.rect)
	for i in self.sprites:
	    self.screen.blit(i.image, i.rect)
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
            self.gs.p1Con.transport.write(myPos)

# PLAYER CONNECTION
class PlayerConnection(Protocol):
    def connectionMade(self):
	# Create player connection
	self.game = GameSpace(p1Con.getConnection(), reactor)
	print("player 1 connection made")
	
    def dataReceived(self, data):
	# server.py has sent data to player 2: update game
    	print 'data received from player2: ', data
        parts = data.split('=') # get label and value
        pos = parts[1].split('\r') #isolate number
        if parts[0] == 'enemy':
            self.game.enemyAvatar.move(int(pos[0]))
		

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


