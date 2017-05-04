# Player 1 Program

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
import time

# PLAYER CONNECTION
class PlayerConnection(Protocol):
	def connectionMade(self):
		# Create player connection
		print("player 1 connection made")
	
	def dataReceived(self, data):
		# server.py has sent data to player 2: update game
		print("data received from player2: ", data)

class PlayerConnectionFactory(Factory):
	def __init__(self):
		self.p1Con = PlayerConnection()

	def buildProtocol(self, addr):
		return self.p1Con

reactor.listenTCP(40402, PlayerConnectionFactory())
reactor.run()


