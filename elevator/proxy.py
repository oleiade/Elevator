#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zmq
import leveldb

from worker import Worker

from elevator.env import Environment


class Backend():
    def __init__(self, db, workers_count=4, **kwargs):
        db_options = kwargs.get('db_options', {}) # NOQA

        self.databases = self.load_databases()

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.socket.bind('inproc://elevator')
        # self.databases = {'default': leveldb.LevelDB(db, **db_options)}
        # self.db = leveldb.LevelDB(db, **db_options)
        # context used to stack datas, and share it
        # between workers. For batches for example.
        self.context = {}
        self.workers_pool = []
        self.init_workers(workers_count, self.context)

    def __del__(self):
        [worker.close() for worker in self.workers_pool]
        self.socket.close()
        self.context.term()

    def load_databases(self):
        env = Environment()  # Singleton, already fulfilled
        server_conf = env['global']

        # Updating databases store with get or created default
        # database
        default_db_path = os.path.join(server_conf['database_store'],
                                  server_conf['default_db'])
        databases = {
            server_conf['default_db']: leveldb.LevelDB(default_db_path)
        }

        # Retrieving every databases from database store on fs,
        # and adding them to backend databases handler.
        databases_names = [db_name for db_name
                           in os.listdir(server_conf['database_store'])
                            if db_name != server_conf['default_db']]
        for database_name in databases_names:
            databases.update({
                database_name: leveldb.LevelDB(os.path.join(server_conf['database_store'], database_name)),
            })
        return databases

    def init_workers(self, count, context):
        pos = 0

        while pos < count:
            worker = Worker(self.zmq_context, self.databases, context)
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
