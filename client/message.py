import msgpack


class Message(str):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        db_uid = kwargs.pop('db_uid')
        command = kwargs.pop('command')
        data = kwargs.pop('data')

        value = [db_uid, command, data]
        return str.__new__(cls, msgpack.packb(value))
