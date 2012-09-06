import ujson as json


class MessageFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Message(object):
    """Handler objects for frontend->backend objects messages"""
    def __init__(self, message):
        if not self.is_valid(message):
            raise MessageFormatError("Bad Message format")
        self.id = message.pop(0)
        self.db_name, self.command, self.data = json.loads(message.pop(0))
        self.reply = [self.id]

    def is_valid(self, message):
        if len(message) != 2:
            return False
        return True
