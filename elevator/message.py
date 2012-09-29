import msgpack
import logging


class MessageFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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
            'DATAS': kwargs.pop('datas', None)
        }

        msg = [id, msgpack.packb(response)]
        return tuple.__new__(cls, msg)
