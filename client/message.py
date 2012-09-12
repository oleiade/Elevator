import msgpack


class MessageOptions(object):
    def __new__(cls, *args, **kwargs):
        compressed = kwargs.pop('compressed', False)

        return msgpack.packb({'compressed': compressed})


class Message(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        db_uid = kwargs.pop('db_uid')
        command = kwargs.pop('command')
        data = kwargs.pop('data')
        compression = kwargs.pop('compression', None)

        msg = msgpack.packb([db_uid, command, data])

        if compression:
            msg = compression(msg)

        return msg
