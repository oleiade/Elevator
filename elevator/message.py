import lz4
import msgpack


class RequestFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __init__(self, message, compressed=False):
        message_content = lz4.loads(message) if compressed else message
        self.db_uid, self.command, self.data = msgpack.unpackb(message_content)



class Response(tuple):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, id, *args, **kwargs):
        status = kwargs.pop('status', 0)
        datas = kwargs.pop('datas', None)

        msg = [id, msgpack.packb([status, datas])]
        return tuple.__new__(cls, msg)
