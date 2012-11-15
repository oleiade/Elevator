# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import msgpack
import logging
import lz4

from .constants import FAILURE_STATUS

activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class MessageFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Request(object):
    """Handler objects for client requests messages

    Format :
    {
        'meta': {...},
        'cmd': 'GET',
        'uid': 'mysuperduperdbuid',
        'args': [...],
    }
    """
    def __init__(self, raw_message):
        self.message = msgpack.unpackb(raw_message)
        self.meta = self.message.get('meta', {})
        activity_logger.debug('<Request ' + str(self.message) + '>')

        try:
            self.db_uid = self.message.get('uid')  # In some case db_uid should be None
            self.command = self.message['cmd']
            self.data = self.message['args']  # __getitem__ will raise if !key
        except KeyError:
            errors_logger.exception("Invalid request message : %s" % self.message)
            raise MessageFormatError("Invalid request message : %r" % self.message)


class ResponseContent(tuple):
    """Handler objects for responses messages

    Format:
    {
        'meta': {
            'status': 1|0|-1,
            'err_code': null|0|1|[...],
            'err_msg': '',
        },
        'datas': [...],
    }
    """
    def __new__(cls, *args, **kwargs):
        response = {
            'datas': cls._format_datas(kwargs['datas']),
        }
        activity_logger.debug('<Response ' + str(response['datas']) + '>')
        msg = msgpack.packb(response)

        if kwargs.pop('compression', False) is True:
            msg = lz4.dumps(msg)

        return msg

    @classmethod
    def _format_datas(cls, datas):
        if datas and not isinstance(datas, (tuple, list)):
            datas = [datas]
        return datas


class ResponseHeader(dict):
    def __new__(cls, *args, **kwargs):
        header = {
            'status': kwargs.pop('status'),
            'err_code': kwargs.pop('err_code', None),
            'err_msg': kwargs.pop('err_msg', None),
            'compression': kwargs.pop('compression', False)
        }
        activity_logger.debug('<ResponseHeader ' + str(header) + '>')

        for key, value in kwargs.iteritems():
            header.update({key: value})

        return msgpack.packb(header)
