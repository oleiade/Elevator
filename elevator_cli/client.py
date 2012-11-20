# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import zmq

from elevator.constants import *

from .io import output_result
from .errors import *
from .helpers import success, fail
from .message import Request, ResponseHeader, Response


class Client(object):
    def __init__(self, *args, **kwargs):
        self.protocol = kwargs.pop('protocol', 'tcp')
        self.endpoint = kwargs.pop('endpoint', '127.0.0.1:4141')
        self.host = "%s://%s" % (self.protocol, self.endpoint)

        self.context = None
        self.socket = None
        self.timeout = kwargs.pop('timeout', 10000)

        self.db_uid = None
        self.db_name = None

        self.setup_socket()

        if self.ping():
            self.connect()
        else:
            failure_msg = 'No elevator server hanging on {0}://{1}'.format(self.protocol, self.endpoint)
            output_result(FAILURE_STATUS, failure_msg)

    def __del__(self):
        self.socket.close()
        self.context.term()

    def ping(self, *args, **kwargs):
        pings = True
        timeout = kwargs.pop('timeout', 1000)
        orig_timeout = self.timeout
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)

        request = Request(db_uid=None, command="PING", args=[])
        self.socket.send_multipart([request])

        try:
            self.socket.recv_multipart()
        except zmq.core.error.ZMQError:
            pings = False

        # Restore original timeout
        self.timeout = orig_timeout
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)

        return pings

    def connect(self, db_name=None, *args, **kwargs):
        db_name = 'default' if db_name is None else db_name
        status, datas = self.send_cmd(None, 'DBCONNECT', [db_name], *args, **kwargs)

        if status == FAILURE_STATUS:
            return status, datas
        else:
            self.db_uid = datas
            self.db_name = db_name

    def setup_socket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect(self.host)

    def teardown_socket(self):
        self.socket.close()
        self.context.term()

    def _process_request(self, command, arguments):
        if command in ["MGET"] and arguments:
            return command, [arguments]
        return command, arguments

    def _process_response(self, req_cmd, res_datas):
        if req_cmd in ["GET", "DBCONNECT", "PING"] and res_datas:
            return res_datas[0]
        return res_datas

    def send_cmd(self, db_uid, command, arguments, *args, **kwargs):
        command, arguments = self._process_request(command, arguments)
        self.socket.send_multipart([Request(db_uid=db_uid,
                                                             command=command,
                                                             args=arguments,
                                                             meta={})],)

        try:
            raw_header, raw_response = self.socket.recv_multipart()
            header = ResponseHeader(raw_header)
            response = Response(raw_response)

            if header.status == FAILURE_STATUS:
                return fail(ELEVATOR_ERROR[header.err_code], header.err_msg)
        except zmq.core.error.ZMQError:
            return fail("TimeoutError", "Server did not respond in time")

        return success(self._process_response(command, response.datas))
