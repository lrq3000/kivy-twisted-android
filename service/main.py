print('LALALALO')

# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol

import sys


class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)


class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

    def __init__(self, app):
        self.app = app


#from kivy.app import App
#from kivy.uix.label import Label


class TwistedServerApp():
    def build(self):
        reactor.listenTCP(8000, EchoFactory(self))

    def handle_message(self, msg):
        #self.label.text = "received:  %s\n" % msg

        print('LALALALU')
        print(msg)
        if msg == "ping":
            msg = "pong"
        if msg == "plop":
            msg = "kivy rocks"
        #self.label.text += "responded: %s\n" % msg
        return msg


def run_server():
    serverapp = TwistedServerApp()
    serverapp.build()

if __name__ == '__main__':
    run_server()
