# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq
import uuid
import time
import logging
import threading

from elevator.api import Handler
from elevator.env import Environment
from elevator.message import Request, ResponseHeader,\
                             ResponseContent, MessageFormatError
from elevator.utils.patterns import enum
from elevator.constants import WORKER_STATUS, WORKER_HALT,\
                               WORKER_LAST_ACTION,\
                               SUCCESS_STATUS, FAILURE_STATUS,\
                               REQUEST_ERROR

from elevator.backend.protocol import ServiceMessage


activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class HaltException(Exception):
    pass


class Worker(threading.Thread):
    def __init__(self, zmq_context, databases, *args, **kwargs):
        threading.Thread.__init__(self)
        self.instructions = {
            WORKER_STATUS: self._status_inst,
            WORKER_HALT: self._stop_inst,
            WORKER_LAST_ACTION: self._last_activity_inst,
        }
        self.uid = uuid.uuid4().hex
        self.env = Environment()
        self.zmq_context = zmq_context

        self.STATES = enum('PROCESSING', 'IDLE', 'STOPPED')
        self.state = self.STATES.IDLE

        # Wire backend and remote control sockets
        self.backend_socket = self.zmq_context.socket(zmq.DEALER)

        self.databases = databases
        self.handler = Handler(databases)

        self.running = False
        self.last_operation = (None, None)

    def wire_remote_control(self):
        """Connects the worker to it's remote control"""
        self.remote_control_socket = self.zmq_context.socket(zmq.DEALER)
        self.remote_control_socket.connect('inproc://remote')
        self.remote_control_socket.send_multipart([ServiceMessage.dumps(self.uid)])

    def _status_inst(self):
        return str(self.state)

    def _stop_inst(self):
        return self.stop()

    def _last_activity_inst(self):
        return self.last_operation

    def handle_instruction(self):
        try:
            serialized_request = self.remote_control_socket.recv_multipart(flags=zmq.NOBLOCK)[0]
            instruction = ServiceMessage.loads(serialized_request)[0]
            response = self.instructions[instruction]()
            self.remote_control_socket.send_multipart([ServiceMessage.dumps(response)],
                                                      flags=zmq.NOBLOCK)

            # If halt instruction succedded, raise HaltException
            # so the worker event loop knows it has to stop
            if instruction == WORKER_HALT and int(response) == SUCCESS_STATUS:
                raise HaltException()
            return
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                return

    def run(self):
        self.backend_socket.connect('inproc://backend')
        self.wire_remote_control()
        msg = None

        while (self.state != self.STATES.STOPPED):
            try:
                self.handle_instruction()
            except HaltException:
                break

            try:
                sender_id, msg = self.backend_socket.recv_multipart(copy=False, flags=zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    continue
            self.state = self.STATES.PROCESSING

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
            self.last_operation = (time.time(), message.db_uid)

            self.backend_socket.send_multipart([sender_id, header, response], flags=zmq.NOBLOCK, copy=False)
            self.state = self.STATES.IDLE

    def stop(self):
        self.state = self.STATES.STOPPED

        if not self.backend_socket.closed:
            self.backend_socket.close()

        activity_logger.info("Gracefully stopping worker %s" % self.uid)
        return str(SUCCESS_STATUS)
