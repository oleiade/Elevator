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
        self.id, self.db_name, self.command = message[:-1]
        self.data = json.loads(message[3])
        self.reply = [self.id]

    def is_valid(self, message):
        if len(message) != 4:
            return False
        return True
