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
	self.myAvatar = Avatar(self, 'images/greensquare.png', 10, 10, 1) #1 for ownership
        self.enemyAvatar = Avatar(self, 'images/globe.png', 10, 20, 0)
	self.sprites = [self.enemyAvatar, self.myAvatar]
	self.allsprites = pygame.sprite.RenderPlain(self.sprites)

        # start game "loop"
        self.reactor.callLater(1/60, self.loop)

    def loop(self):
	for event in pygame.event.get():
	    if event.type == QUIT:
		pygame.quit()
		os._exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.myAvatar.move(self.myAvatar.rect.x - 5) #move left
                elif event.key == pygame.K_RIGHT:
                    self.myAvatar.move(self.myAvatar.rect.x + 5) #move right
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
	pygame.sprite.Sprite.__init__(self)
	self.image, self.rect = load_image('images/booth.jpg') 
	self.rect.topleft = 0, 0
    def tick(self):
	i = 1

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


# PLAYER 2 CONNECTION
class PlayerConnection(Protocol):
    def connectionMade(self):
	# Create player connection
	print'player 2 connection made'
	self.game = GameSpace(p2Con.getConnection(),reactor)
#	lc = LoopingCall(game.loop)
#	lc.start(1/60)

    def dataReceived(self, data):
	# server.py has sent data to player 1: update game
	print 'data received from player1: ', data
        parts = data.split('=') #get label and value
        pos = parts[1].split('\r') #isolate number
        if parts[0] == 'enemy':
            self.game.enemyAvatar.move(int(pos[0]))


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

