import msgpack
import logging

from .constants import FAILURE_STATUS, SUCCESS_STATUS,\
                                   WARNING_STATUS


class MessageFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def failure(error_code, error_msg):
    return (FAILURE_STATUS, [error_code, error_msg])


def success(content):
    return (SUCCESS_STATUS, content)


def warning(error_code, error_msg, content):
    return (WARNING_STATUS, [error_code, error_msg, content])


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __init__(self, raw_message, compressed=False):
        errors_logger = logging.getLogger("errors_logger")
        message = msgpack.unpackb(raw_message)
        try:
            self.db_uid = message.pop('DB_UID')
            self.command = message.pop('COMMAND')
            self.data = message.pop('ARGS')
        except KeyError:
            errors_logger.exception("Invalid request message : %s" %
                                    message)
            raise MessageFormatError("Invalid request message")


class Response(tuple):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, id, *args, **kwargs):
        response = {
            'STATUS': kwargs.pop('status', 0),
            'DATAS': kwargs.pop('datas', [])
        }

        response['DATAS'] = cls._format_datas(response['DATAS'])
        msg = [id, msgpack.packb(response)]
        return tuple.__new__(cls, msg)

    @classmethod
    def _format_datas(cls, datas):
        if datas and not isinstance(datas, (tuple, list)):
            datas = [datas]
        return datas
