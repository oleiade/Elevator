#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import leveldb
import threading
import ujson as json

from api import Handler
from worker import Worker
from utils.patterns import enum
from utils.decorators import cached_property


class Backend():
    def __init__(self, db, workers_count=4):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.bind('inproc://leveldb')
        self.db = leveldb.LevelDB(db)
        self.workers_pool = []
        self.init_workers(workers_count)


    def __del__(self):
        [worker.close() for worker in self.workers_pool]
        self.socket.close()
        self.context.term()


    def init_workers(self, count):
        pos = 0

        while pos < count:
            worker = Worker(self.context, self.db)
            worker.start()
            self.workers_pool.append(worker)
            pos += 1


class Frontend():
    def __init__(self, host):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREP)
        self.socket.bind(host)

    def __del__(self):
        self.socket.close()
        self.context.term()
