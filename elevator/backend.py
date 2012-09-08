import zmq
import threading

from time import sleep

from .env import Environment
from .api import Handler
from .message import Request, RequestFormatError, Response
from .db import DatabasesHandler
from .utils.patterns import enum


class Worker(threading.Thread):
    def __init__(self, zmq_context, databases, context, *args, **kwargs):
        threading.Thread.__init__(self)
        self.STATES = enum('RUNNING', 'IDLE', 'STOPPED')
        self.zmq_context = zmq_context
        self.state = self.STATES.RUNNING
        self.databases = databases
        self.context = context
        self.env = Environment()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.handler = Handler(databases, context)

    def run(self):
        self.socket.connect('inproc://elevator')
        msg = None

        while (self.state == self.STATES.RUNNING):
            try:
                msg = self.socket.recv_multipart()
            except zmq.ZMQError:
                self.state = self.STATES.STOPPED
                continue

            self.processing = True

            try:
                message = Request(msg)
            except RequestFormatError:
                value = 'None'
                reply = [msg[0], value]
                self.socket.send_multipart(reply)
                continue

            # Handle message, and execute the requested
            # command in leveldb
            status, datas = self.handler.command(message, self.context, env=self.env)
            response = Response(message.id, status=status, datas=datas)
            self.socket.send_multipart(response)
            self.processing = False

    def close(self):
        self.running = False

        while self.processing:
            sleep(1)

        self.socket.close()


class WorkersPool():
    def __init__(self, workers_count=4, **kwargs):
        env = Environment()
        self.databases = DatabasesHandler(env['global']['database_store'])

        # context used to stack datas, and share it
        # between workers. For batches for example.
        self.context = {}
        self.pool = []

        self.zmq_context = zmq.Context()
        self.socket = self.zmq_context.socket(zmq.XREQ)
        self.socket.bind('inproc://elevator')
        self.init_workers(workers_count, self.context)

    def __del__(self):
        for worker in self.pool:
            worker.close()

        del self.pool
        self.socket.close()
        self.context.term()

    def init_workers(self, count, context):
        pos = 0

        while pos < count:
            worker = Worker(self.zmq_context, self.databases, context)
            worker.start()
            self.pool.append(worker)
            pos += 1
