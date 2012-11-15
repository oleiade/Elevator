# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import zmq

from elevator.constants import *

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

        self.connect()

    def __del__(self):
        self.socket.close()
        self.context.term()

    def connect(self, db_name=None, *args, **kwargs):
        self.setup_socket()
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

    def _format_response(self, req_cmd, res_datas):
        if req_cmd == "GET" or "DBCONNECT" and res_datas:
            return res_datas[0]
        return res_datas

    def send_cmd(self, db_uid, command, arguments, *args, **kwargs):
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

        return success(self._format_response(command, response.datas))
