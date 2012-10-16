from __future__ import absolute_import

import msgpack
import logging

from .constants import FAILURE_STATUS

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

        try:
            self.meta = self.message.get('meta', {})
            self.db_uid = self.message['uid']
            self.command = self.message['cmd']
            self.data = self.message['args']  # __getitem__ will raise if !key
        except KeyError:
            errors_logger.exception("Invalid request message : %s" % self.message)
            raise MessageFormatError("Invalid request message : %r" % self.message)

    def __str__(self):
        return '<Request ' + self.command + ' ' + '%r' % str(self.data) + '>'


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
        cls.response = {
            'datas': cls._format_datas(kwargs['datas']),
        }

        return msgpack.packb(cls.response)

    def __str__(cls):
        return '<Response ' + str(cls.response) + '>'

    @classmethod
    def _format_datas(cls, datas):
        if datas and not isinstance(datas, (tuple, list)):
            datas = [datas]
        return datas


class ResponseHeader(dict):
    def __new__(cls, *args, **kwargs):
        cls.header = {
            'status': kwargs.pop('status'),
            'err_code': kwargs.pop('err_code', None),
            'err_msg': kwargs.pop('err_msg', None),
        }

        for key, value in kwargs.iteritems():
            cls.header.update({key: value})

        return msgpack.packb(cls.header)

    def __str__(cls):
        return '<RequestHeader ' + str(cls.header) + '>'
