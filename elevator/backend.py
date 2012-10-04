import zmq
import logging
import threading

from time import sleep

from .constants import FAILURE_STATUS
from .env import Environment
from .api import Handler
from .message import Request, MessageFormatError, Response
from .db import DatabasesHandler
from .utils.patterns import enum


class Worker(threading.Thread):
    def __init__(self, zmq_context, databases, *args, **kwargs):
        threading.Thread.__init__(self)
        self.STATES = enum('RUNNING', 'IDLE', 'STOPPED')
        self.zmq_context = zmq_context
        self.state = self.STATES.RUNNING
        self.databases = databases
        self.env = Environment()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.handler = Handler(databases)
        self.processing = False
        self.sleep_time = 0.1
        self.errors_logger = logging.getLogger("errors_logger")

    def run(self):
        self.socket.connect('inproc://elevator')
        msg = None

        while (self.state == self.STATES.RUNNING):
            try:
                msg_id, msg = self.socket.recv_multipart(flags=zmq.NOBLOCK, copy=False)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    sleep(self.sleep_time)
                else:
                    self.state = self.STATES.STOPPED
                    self.errors_logger.warning('Worker %r encountered and error,'
                                               ' and was forced to stop' % self.ident)
                continue

            self.processing = True

            try:
                message = Request(msg)
            except MessageFormatError:
                response = Response(msg_id, status=FAILURE_STATUS, datas=None)
                self.socket.send_multipart(response, copy=False)
                continue

            # Handle message, and execute the requested
            # command in leveldb
            status, datas = self.handler.command(message)
            response = Response(msg_id, status=status, datas=datas)
            self.socket.send_multipart(response, zmq.NOBLOCK, copy=False)
            self.processing = False

    def close(self):
        self.state = self.STATES.STOPPED
        self.join()
        self.socket.close()


class WorkersPool():
    def __init__(self, workers_count=4, **kwargs):
        env = Environment()
        database_store = env['global']['database_store']
        databases_storage = env['global']['databases_storage_path']
        self.databases = DatabasesHandler(database_store, databases_storage)
        self.pool = []

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.socket.bind('inproc://elevator')
        self.init_workers(workers_count)

    def __del__(self):
        for worker in self.pool:
            worker.close()

        self.socket.close()

    def init_workers(self, count):
        pos = 0

        while pos < count:
            worker = Worker(self.zmq_context, self.databases)
            worker.start()
            self.pool.append(worker)
            pos += 1
