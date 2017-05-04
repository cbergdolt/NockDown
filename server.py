from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue

# INIT CONNECTION
class InitConnection(Protocol):
	def connectionMade(self):
		print("init connection made")
		
	def dataReceived(self, data):
		print("")

class InitConnectionFactory(Factory):
	def __init__(self):
		self.initCon = InitConnection()

	def buildProtocol(self, addr):
		return self.initCon

	def returnConnection(self):
		return self.initCon

# PLAYER2 CONNECTION
class Player2Connection(Protocol):
	def __init__(self, initConnection):
		self.initConnection = initConnection
		self.q = DeferredQueue()

	def connectionMade(self):
		# Player 2 connection is made: start listening for player 1 connection
		p1Factory = Player1ConnectionFactory(self)
		self.player1Con = p1Factory.returnConnection()
		reactor.listenTCP(42402, p1Factory) 
		
		# Send message to work.py to begin data connection
		self.initConnection.transport.write("send p1")

	def dataReceived(self, data):
		# player 2 has sent data to server.py: put on queue
		self.q.put(data)

	def forwardData(self, data):
		# write data sent from client through data connection
		self.p1Con.transport.write(data)
		self.q.get().addCallback(self.forwardData)
	
	def startForwarding(self):
		# add forwardData to object on queue
		self.q.get().addCallback(self.forwardData)

class Player2ConnectionFactory(Factory):
	def __init__(self, initConnection):
		self.p2Con = Player2Connection(initConnection)

	def buildProtocol(self, addr):
		return self.p2Con



# PLAYER1 CONNECTION
class Player1Connection(Protocol):
	def __init__(self, p2Connection):
		self.p2Connection = p2Connection

	def connectionMade(self):
		self.p2Connection.startForwarding()

	def dataReceived(self, data):
		# Player 1 has sent data to server.py: write to player 2
		self.p2Connection.transport.write(data)

class Player1ConnectionFactory(Factory):
	def __init__(self, p2Connection):
		self.p1Con = Player1Connection(p2Connection)
	
	def returnConnection(self):
		return self.p1Con

	def buildProtocol(self, addr):
		return self.p1Con


initFactory = InitConnectionFactory()
init = initFactory.returnConnection()
player2 = Player2ConnectionFactory(init)
reactor.listenTCP(41402, player2)	# Start listening for player2 connection
reactor.listenTCP(40402, initFactory)
reactor.run()




