# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import msgpack
import logging


errors_logger = logging.getLogger("errors_logger")


class MessageFormatError(Exception):
    pass


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        try:
            content = {
                'meta': kwargs.pop('meta', {}),
                'uid': kwargs.get('db_uid'),  # uid can eventually be None
                'cmd': kwargs.pop('command'),
                'args': kwargs.pop('args'),
            }
        except KeyError:
            raise MessageFormatError("Invalid request format : %s" % str(kwargs))

        return msgpack.packb(content)


class Response(object):
    def __init__(self, raw_message, *args, **kwargs):
        message = msgpack.unpackb(raw_message)

        try:
            self.datas = message['datas']
        except KeyError:
            errors_logger.exception("Invalid response message : %s" %
                                    message)
            raise MessageFormatError("Invalid response message")


class ResponseHeader(object):
    def __init__(self, raw_header):
        header = msgpack.unpackb(raw_header)

        try:
            self.status = header.pop('status')
            self.err_code = header.pop('err_code')
            self.err_msg = header.pop('err_msg')
        except KeyError:
            errors_logger.exception("Invalid response header : %s" %
                                    header)
            raise MessageFormatError("Invalid response header")

        for key, value in header.iteritems():
            setattr(self, key, value)
