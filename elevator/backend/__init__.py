# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq

from elevator.db import DatabasesHandler
from elevator.env import Environment

from .supervisor import Supervisor


class Backend():
    def __init__(self, workers_count=4, **kwargs):
        env = Environment()
        database_store = env['global']['database_store']
        databases_storage = env['global']['databases_storage_path']
        self.databases = DatabasesHandler(database_store, databases_storage)

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.DEALER)
        self.socket.bind('inproc://backend')
        self.supervisor = Supervisor(self.zmq_context, self.databases)

        self.supervisor.init_workers(workers_count)

    def __del__(self):
        del self.supervisor
        self.socket.close()
