# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq
import uuid
import logging
import threading

from .db import DatabasesHandler
from .env import Environment
from .api import Handler
from .constants import FAILURE_STATUS, REQUEST_ERROR, WORKER_HALT
from .message import Request, MessageFormatError, ResponseContent, ResponseHeader
from .utils.snippets import sec_to_ms
from .utils.patterns import enum

activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class HaltException(Exception):
    pass


class Worker(threading.Thread):
    def __init__(self, zmq_context, databases, *args, **kwargs):
        threading.Thread.__init__(self)
        self.instructions = {
            'STATE': self.state_inst,
        }
        self.uid = uuid.uuid4().hex
        self.env = Environment()
        self.zmq_context = zmq_context

        self.STATES = enum('RUNNING', 'IDLE', 'STOPPED')
        self.state = self.STATES.RUNNING

        # Wire backend and remote control sockets
        self.backend_socket = self.zmq_context.socket(zmq.DEALER)

        self.databases = databases
        self.handler = Handler(databases)

        self.running = False

    def wire_remote_control(self):
        """Connects the worker to it's remote control"""
        self.remote_control_socket = self.zmq_context.socket(zmq.DEALER)
        # self.remote_control_socket.setsockopt(zmq.IDENTITY, self.uid)
        self.remote_control_socket.connect('inproc://remote')
        self.remote_control_socket.send_multipart([self.uid])

    def state_inst(self):
        return str(self.state)

    def handle_instruction(self):
        try:
            instruction = self.remote_control_socket.recv_multipart(flags=zmq.NOBLOCK)[0]
            response = self.instructions[instruction]()
            return self.remote_control_socket.send_multipart([response], flags=zmq.NOBLOCK)
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                return

    def run(self):
        self.backend_socket.connect('inproc://backend')
        self.wire_remote_control()
        msg = None

        while (self.state == self.STATES.RUNNING):
            self.handle_instruction()

            try:
                sender_id, msg = self.backend_socket.recv_multipart(copy=False, flags=zmq.NOBLOCK)
                # If worker pool sends a WORKER_HALT, then close
                # and return to stop execution
                if sender_id.bytes == WORKER_HALT:  # copy=False -> zmq.Frame
                    raise HaltException("Gracefully stopping worker %r" % self.ident)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    continue
                else:
                    self.state = self.STATES.STOPPED
                    errors_logger.warning('Worker %r encountered and error,'
                                          ' and was forced to stop' % self.ident)
                    return
            except HaltException as e:
                activity_logger.info(e)
                return self.close()

            self.running = True

            try:
                message = Request(msg)
            except MessageFormatError as e:
                errors_logger.exception(e.value)
                header = ResponseHeader(status=FAILURE_STATUS,
                                        err_code=REQUEST_ERROR,
                                        err_msg=e.value)
                content = ResponseContent(datas={})
                self.backend_socket.send_multipart([sender_id, header, content], copy=False)
                continue

            # Handle message, and execute the requested
            # command in leveldb
            header, response = self.handler.command(message)

            self.backend_socket.send_multipart([sender_id, header, response], flags=zmq.NOBLOCK, copy=False)
            self.running = False

    def close(self):
        self.state = self.STATES.STOPPED

        if not self.backend_socket.closed:
            self.backend_socket.close()


class Supervisor(object):
    """A remote control to lead them all

    Exposes an internal api to talk to database workers and
    give them orders.
    """
    def __init__(self, zmq_context, databases_store, timeout=3):
        self.databases_store = databases_store
        self.workers = {}
        self.timeout = sec_to_ms(timeout)

        self.zmq_context = zmq_context
        self.socket = zmq_context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.bind('inproc://remote')

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def __del__(self):
        while any(worker.isAlive() for worker in self.pool):
            self.socket.send_multipart([WORKER_HALT, ""])

        for worker in self.pool:
            worker.join()

    def command(self, instruction, workers_ids=None):
        """Command an action to workers.

        An optional list of workers ids can be provided
        as an argument, in order to restrain the command
        to specific workers.
        """
        workers_ids = workers_ids or self.workers.iterkeys()
        max_retries = 3
        responses = []

        for worker_id in workers_ids:
            if worker_id in self.workers:
                self.socket.send_multipart([self.workers[worker_id], instruction], flags=zmq.NOBLOCK)

                retried = 0
                while retried <= max_retries:
                    sockets = dict(self.poller.poll(self.timeout))

                    if sockets:
                        if sockets.get(self.socket) == zmq.POLLIN:
                            responses.append(self.socket.recv_multipart(flags=zmq.NOBLOCK)[1])
                            break
                    else:
                        retried += 1

                if retried == max_retries:
                    err_msg = "Instruction %s sent to %s failed. Retried %d times"
                    errors_logger.error(err_msg % (instruction, worker_id, retried))

        return responses

    def statuses(self):
        return self.command("STATE")

    def init_workers(self, count):
        pos = 0

        while pos < count:
            # Start a worker
            worker = Worker(self.zmq_context, self.databases_store)
            worker.start()
            socket_id, worker_id = self.socket.recv_multipart()
            self.workers[worker_id] = socket_id
            pos += 1


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
        del self.workers_pool
        self.socket.close()
