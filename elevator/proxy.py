#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import leveldb

from worker import Worker


class Backend():
    def __init__(self, db, workers_count=4, **kwargs):
        db_options = kwargs.get('db_options', {})

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.socket.bind('inproc://leveldb')
        self.db = leveldb.LevelDB(db, **db_options)
        # context used to stack datas, and share it
        # between workers. For batches for example.
        self.context = {}
        self.workers_pool = []
        self.init_workers(workers_count, self.context)

    def __del__(self):
        [worker.close() for worker in self.workers_pool]
        self.socket.close()
        self.context.term()

    def init_workers(self, count, context):
        pos = 0

        while pos < count:
            worker = Worker(self.zmq_context, self.db, context)
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
