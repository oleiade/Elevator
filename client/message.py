import ujson as json


class Message(str):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, *args, **kwargs):
        cmd_id = kwargs.pop('id')
        db_name = kwargs.pop('db_name')
        command = kwargs.pop('command')
        data = kwargs.pop('data')

        value = [cmd_id, db_name, command, data]
        return str.__new__(cls, json.dumps(value))
