#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import md5
import zmq
import leveldb

from worker import Worker

from elevator.env import Environment
from elevator.db import DatabasesHandler


class Backend():
    def __init__(self, db, workers_count=4, **kwargs):
        env = Environment()
        db_options = kwargs.get('db_options', {}) # NOQA
        self.databases = DatabasesHandler(env['global']['database_store'])

        # context used to stack datas, and share it
        # between workers. For batches for example.
        self.context = {}
        self.workers_pool = []


        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.socket.bind('inproc://elevator')
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
        default_db_name = server_conf['default_db']
        default_db_uid = md5.new(default_db_name).digest()
        default_db_path = os.path.join(server_conf['database_store'],
                                       default_db_name)
        databases = {
            'index': {default_db_name: default_db_uid},
            default_db_uid: leveldb.LevelDB(default_db_path),
        }

        # Retrieving every databases from database store on fs,
        # and adding them to backend databases handler.
        for db_name in os.listdir(server_conf['database_store']):
            if db_name != server_conf['default_db']:
                db_path = os.path.join(server_conf['database_store'], db_name)
                db_uid = md5.new(db_name).digest()
                databases['index'].update({db_name: db_uid})
                databases.update({db_uid: leveldb.LevelDB(db_path)})

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
