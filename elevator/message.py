import msgpack
import logging


errors_logger = logging.getLogger("errors_logger")


class MessageFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Request(object):
    """Handler objects for frontend->backend objects messages"""
    def __init__(self, raw_message, compressed=False):
        self.message = msgpack.unpackb(raw_message)
        try:
            self.db_uid = self.message.get('DB_UID')
            self.command = self.message.get('COMMAND')
            self.data = self.message['ARGS']  # __getitem__ will raise if !key
        except KeyError:
            errors_logger.exception("Invalid request message : %s" %
                                    self.message)
            raise MessageFormatError("Invalid request message")

    def __str__(self):
        return '<Request ' + str(self.message) + '>'


class Response(tuple):
    """Handler objects for frontend->backend objects messages"""
    def __new__(cls, id, *args, **kwargs):
        cls.response = {
            'STATUS': kwargs.get('status', 0),
            'DATAS': kwargs.get('datas', [])
        }

        cls.response['DATAS'] = cls._format_datas(cls.response['DATAS'])
        msg = [id, msgpack.packb(cls.response)]
        return tuple.__new__(cls, msg)

    def __str__(cls):
        return '<Response ' + str(cls.response) + '>'

    @classmethod
    def _format_datas(cls, datas):
        if datas and not isinstance(datas, (tuple, list)):
            datas = [datas]
        return datas

