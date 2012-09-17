import msgpack


class Message(object):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        db_uid = kwargs.pop('db_uid')
        command = kwargs.pop('command')
        data = kwargs.pop('data')

        return msgpack.packb([db_uid, command, data])
