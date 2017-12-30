#!/usr/bin/python

print('LALALALI')

__version__ = '0.1'


# install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


# A simple Client that send messages to the echo server
from twisted.internet import reactor, protocol

import time, sys
from threading import Thread, Lock
import logging

logger = logging.getLogger(__name__)


class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        self.factory.app.print_message(data)


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        self.app.print_message("connection lost")

    def clientConnectionFailed(self, conn, reason):
        self.app.print_message("connection failed")


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout


# A simple kivy App, with a textbox to enter messages, and
# a large label to display all the messages received from
# the server
class TwistedClientApp(App):
    connection = None

    def build(self):
        root = self.setup_gui()
        self.connect_to_server()
        return root

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        self.label = Label(text='connecting...\n')
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.textbox)
        return self.layout

    def connect_to_server(self):
        reactor.connectTCP('localhost', 8000, EchoFactory(self))

    def on_connection(self, connection):
        self.print_message("connected successfully!")
        self.connection = connection

    def send_message(self, *args):
        msg = self.textbox.text
        if msg and self.connection:
            self.connection.write(str(self.textbox.text))
            self.textbox.text = ""

    def print_message(self, msg):
        self.label.text += msg + "\n"


class WebserverService(App):
    def build(self):
        print('LAUNCHING')
        self.start_service()

    def start_service(self):
        if sys.platform == 'android' or sys.platform == 'linux3':
            from android import AndroidService
            service = AndroidService('Twisted2Webserver', 'running')  # this will launch what is in the folder service/main.py as a service
            service.start('Twisted2Webserver service started')
            self.service = service
        else:
            from service.main import run_server
            logger.debug("Starting server")
            t = Thread(target=run_server)
            t.daemon = True
            t.start()
            logger.debug("Waiting for server")
            time.sleep(0.1)
            logger.debug("Server started")

    def stop_service(self):
        if self.service:
            self.service.stop()
            self.service = None

    def on_stop(self):  # TODO: does not work! We need to close the service on leaving!
        self.stop_service()


if __name__ == '__main__':
    webserver = WebserverService()
    webserver.build()
    #webserver.run()
    time.sleep(0.1)
    webserver.stop_service()  # workaround because service might still be running on exit
    time.sleep(0.5)
    webserver.start_service()
    time.sleep(2.0)
    TwistedClientApp().run()
