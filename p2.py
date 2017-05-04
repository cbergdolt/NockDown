# Player 2 Program

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.protocols.basic import LineReceiver

# PLAYER 2 CONNECTION
class PlayerConnection(Protocol):
	def connectionMade(self):
		# Create player connection
		print("player 2 connection made")
		
	def dataReceived(self, data):
		# server.py has sent data to player 1: update game
		print("data received from player1: ", data)

class PlayerConnectionFactory(ClientFactory):
	def __init__(self):
		self.p2Con = PlayerConnection()

	def buildProtocol(self, addr):
		return self.p2Con


if __name__ == "__main__":
	reactor.connectTCP("ash.campus.nd.edu", 40402, PlayerConnectionFactory())
	reactor.run()

