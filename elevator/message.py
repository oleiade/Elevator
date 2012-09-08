import msgpack


class RequestFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __init__(self, message):
        if not self.is_valid(message):
            raise RequestFormatError("Bad Message format")
        self.id = message[0]
        self.db_uid, self.command, self.data = msgpack.unpackb(message[1])

    def is_valid(self, message):
        if len(message) != 2:
            return False
        return True


class Response(tuple):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, id, *args, **kwargs):
        status = kwargs.pop('status', 0)
        datas = kwargs.pop('datas', None)

        msg = [id, msgpack.packb([status, datas])]
        return tuple.__new__(cls, msg)
