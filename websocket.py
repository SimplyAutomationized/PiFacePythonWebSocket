__author__ = 'Nate Rees'
import sys, json
from twisted.internet import reactor, ssl, protocol
from twisted.python import log
from OpenSSL import SSL
from twisted.web.server import Site
from twisted.web.static import File
from twisted.application import service, strports
from twisted.web.guard import DigestCredentialFactory

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from autobahn.twisted.resource import WebSocketResource, HTTPChannelHixie76Aware

from twisted.web.util import redirectTo
from twisted.python import log
from twisted.web.resource import Resource
from time import sleep
from ButtonListener import Buttons
from PlugPoller import PlugPoller
class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            data = json.loads(payload)
            if(data["Output"]):
                output = data["Output"]
                current = factory.lighting.output_status()[int(output)]
                newval = not int(current)
                print(output,' ',current,' ',newval)
                factory.lighting.output_cmd(int(output), newval, False)


    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
        self.clients = []
        self.lighting = Buttons()
        self.lighting.button1Callback = self.broadcast
        self.lighting.button2Callback = self.broadcast
        self.lighting.start()
        self.plugs = PlugPoller('10.10.55.25', 8080)
        self.plugs.statusChangeCallback = self.broadcast
        self.lighting.button2LongPressCallback = self.plugs.toggleAll

    def register(self, client):
        if client not in self.clients:
            client.sendMessage(json.dumps([{"Outputs":self.lighting.output_status()},
                                {"Inputs":self.lighting.input_status()},
                                {"Lamps":self.plugs.getstatus()}]))
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))

if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False
    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key','keys/server.crt')
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory("wss://localhost:9000", debug=True, debugCodePaths=True)
    factory.protocol = BroadcastServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory, contextFactory)
    webdir = File("web/")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)
    web.protocol = HTTPChannelHixie76Aware
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    factory.setProtocolOptions(allowHixie76=True)
    #reactor.listenTCP(443, web)
    reactor.listenSSL(443,web,contextFactory)
    reactor.run()
    factory.lighting.stop()
