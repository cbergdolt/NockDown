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
	def __init__(self, p2Con):
		# Add network connection
		self.p2Con = p2Con

		# Initialize window settings
		pygame.init()
		pygame.key.set_repeat(100, 30)
		self.black = 30, 144, 255
		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)

		# Initialize game objects
		self.clock = pygame.time.Clock()
		self.myAvatar = Avatar(self)
		self.sprites = [self.myAvatar]
		self.allsprites = pygame.sprite.RenderPlain(self.sprites)

	def loop(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit
		for sprite in self.sprites:
			sprite.tick()

		# Update screen
		self.allsprites.update()
		self.screen.fill(self.black)
		for i in self.sprites:
			self.screen.blit(i.image, i.rect)
		self.allsprites.draw(self.screen)
		pygame.display.flip

# AVATAR CLASS
class Avatar(pygame.sprite.Sprite):
	def __init__(self, gs):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('images/globe.png')
		self.rect.topleft = 10, 10

	def tick(self):
		i = 5


# PLAYER 2 CONNECTION
class PlayerConnection(Protocol):
	def connectionMade(self):
		# Create player connection
		print("player 2 connection made")
		game = GameSpace(p2Con.getConnection())
		lc = LoopingCall(game.loop)
		lc.start(1/60)

	def dataReceived(self, data):
		# server.py has sent data to player 1: update game
		print("data received from player1: ", data)

class PlayerConnectionFactory(ClientFactory):
	def __init__(self):
		self.p2Con = PlayerConnection()
	
	def getConnection(self):
		return self.p2Con

	def buildProtocol(self, addr):
		return self.p2Con


if __name__ == "__main__":
	p2Con = PlayerConnectionFactory()
	reactor.connectTCP("ash.campus.nd.edu", 40402, p2Con)
	reactor.run()

