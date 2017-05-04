# Player 1 Program

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue

# PLAYER 2 CONNECTION
class Player2Connection(Protocol):
	def connectionMade(self):
		# Create player 2 connection
		print("player 2 connection made")
	
	def dataReceived(self, data):
		# server.py has sent data to player 2: update game
		print("data sent to player2: ", data)

class Player2ConnectionFactory(ClientFactory):
	def __init__(self):
		self.p2Con = Player2Connection()

	def buildProtocol(self, addr):
		return self.p2Con

reactor.connectTCP("ash.campus.nd.edu", 41402, Player2ConnectionFactory())
reactor.run()


