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
	def __init__(self, p1Con):
		# Add network connection
		self.p1Con = p1Con

		# Initialize window settings
		pygame.init()
		pygame.key.set_repeat(100, 30)
		self.back = 255, 255, 255 
		self.size = self.width, self.height = 640, 480
		self.screen = pygame.display.set_mode(self.size)
		
		# Initialize game objects
		self.clock = pygame.time.Clock()
		self.background = Background(self)
		self.myAvatar = Avatar(self)
		self.sprites = [self.background, self.myAvatar] # contains list of objects
		self.allsprites = pygame.sprite.RenderPlain(self.sprites)
		
	def loop(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				self.p1Con.transport.write("button pressed")
		for sprite in self.sprites:
			sprite.tick()

		# Update screen
		self.allsprites.update()
		self.screen.fill(self.back)
		for i in self.sprites:
			self.screen.blit(i.image, i.rect)
		self.allsprites.draw(self.screen)
		pygame.display.flip()
		
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
	def __init__(self, gs):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('images/greensquare.png')
		self.rect.topleft = 10, 10

	def tick(self):
		i = 4

# PLAYER CONNECTION
class PlayerConnection(Protocol):
	def connectionMade(self):
		# Create player connection
		game = GameSpace(p1Con.getConnection())
		lc = LoopingCall(game.loop)
		lc.start(1/60)
		print("player 1 connection made")
	
	def dataReceived(self, data):
		# server.py has sent data to player 2: update game
		print("data received from player2: ", data)
		

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


