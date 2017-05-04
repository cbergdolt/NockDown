# Player 1 Program

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue


# INIT CONNECTION
class InitConnection(Protocol):
	def connectionMade(self):
		print("init connection made")

	def dataReceived(self, data):
		if (data == 'send p1'):
			reactor.connectTCP("ash.campus.nd.edu", 42402, Player1ConnectionFactory())

class InitConnectionFactory(ClientFactory):
	def __init__(self):
		self.initCon = InitConnection()

	def buildProtocol(self, addr):
		return self.initCon

# PLAYER 1 CONNECTION
class Player1Connection(Protocol):
	def connectionMade(self):
		# Create service connection
		print("player 1 connection made")
	
	def dataReceived(self, data):
		# server.py has sent data to player 1: update game
		print("data sent to player1: ", data)

class Player1ConnectionFactory(ClientFactory):
	def __init__(self):
		self.p1Con = Player1Connection()

	def buildProtocol(self, addr):
		return self.p1Con

if __name__ == "__main__":
	reactor.connectTCP("ash.campus.nd.edu", 40402, InitConnectionFactory())
	reactor.run()


