# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import zmq

from elevator.constants import *

from .message import Request, ResponseHeader, Response


def send_cmd(self, command, *args, **kwargs):
    global socket
    global timeout

    socket.send_multipart([Request(db_uid=db_uid,
                                   command=command,
                                   args=arguments,
                                   meta={})],)

    try:
        raw_header, raw_response = socket.recv_multipart()
        header = ResponseHeader(raw_header)
        response = Response(raw_response)

        if header.status == FAILURE_STATUS:
            raise ELEVATOR_ERROR[header.err_code](header.err_msg)
    except zmq.core.error.ZMQError:
        # Restore original timeout and raise
        raise TimeoutError("Timeout : Server did not respond in time")

    return response.datas
