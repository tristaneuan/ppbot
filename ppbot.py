"""ppbot.py

A modular python bot that utilizes/will utilize postgresql as a data source.

TODO: Lots
"""
# database stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import irclib
from handlers.modulehandler import ModuleHandler
from handlers.eventhandler import EventHandler

from models.configuration import Configuration
from models.network import Network
from models.server import Server
from models.channel import Channel

from db import Db

# traceback shit
import inspect
import traceback
import sys
import string

#irclib.DEBUG = True

class ppbot:
    
    def __init__ (self):
        """Create an IRC object and do some initializations.
        Need to set handlers for events that may occur so that modules will be able to
        use them.
        
        """
    
        self.irc = irclib.IRC()
        self.servers = []
        
        
        # initialize the databse
        self.engine = Db.engine
        self.session = Db.session
        
        
        # load configuration
        self.config = Configuration()
        self.config.session_start()
        
        # initialize the module handler
        self.module_handler = ModuleHandler(self.servers)
        # initialize the event handler
        self.event_handler = EventHandler(self.servers)
        self.event_handler.module_handler = self.module_handler
        
        # send all events to the event handler dispatcher
        self.irc.add_global_handler('all_events', self.event_handler.dispatcher)
        
        # load the default modules and auto-run modules
        self.load_modules()
      
        
    def connect(self):
        """ Create a server object, connect and join the channel. """

        networks = Network().val()

        for network in networks:
            # connect to the server
            server = self.irc.server()
            self.servers.append(server)
            server.server_config = network

            # TODO: should be using a queue for the servers to go through, 
            # since it could be possible to have more than one server to 
            # try to connect to.
            server_config = network.servers[0]
            server.connect(server_config.address, server_config.port, server_config.nickname, server_config.password, ircname=server_config.realname)

        # jump into an infinite loop
        self.irc.process_forever()
		
    def load_modules(self):
        """ for now we will manually load modules, but this will eventually 
        call the database for what modules to auto-load
            
        """
        
        core = self.module_handler.load('Core')
        core.module_handler = self.module_handler

        self.module_handler.load('Irc')
        self.module_handler.load('Weather')
        self.module_handler.load('Urlparser')
        #self.module_handler.load('Chatbot')
        self.module_handler.load('Riftstatus')

if __name__ == "__main__":
    bot = ppbot()
    bot.connect()
