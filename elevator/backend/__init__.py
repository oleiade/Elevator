# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq

from .supervisor import Supervisor
from .atm import Majordome


class Backend(object):
    def __init__(self, db_handler, config, **kwargs):
        self.config = config
        self.databases = db_handler

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.DEALER)
        self.socket.bind('inproc://backend')

        self.supervisor = Supervisor(self.zmq_context, self.databases)
        self.supervisor.init_workers(config['workers'])

        self.start_majordome()

    def __del__(self):
        self.supervisor.stop_all()
        self.stop_majordome()
        self.socket.close()

    def start_majordome(self):
        if int(self.config['majordome_interval']) > 0:
            self.majordome = Majordome(self.supervisor,
                                       self.databases,
                                       int(self.config['majordome_interval']))
            self.majordome.start()

    def stop_majordome(self):
        if hasattr(self, 'majordome'):
            self.majordome.cancel()
            self.majordome.join()
            del self.majordome
