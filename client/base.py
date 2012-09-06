import zmq

from .message import Message


class Client(object):
    def __init__(self, *args, **kwargs):
        self.bind = kwargs.pop('bind', '127.0.0.1')
        self.port = kwargs.pop('port', '4141')
        self.db_name = kwargs.pop('db_name', 'default')
        self.timeout = kwargs.pop('timeout', 10 * 10000)
        self.host = "tcp://%s:%s" % (self.bind, self.port)
        self._connect()

    def __del__(self):
        self._close()

    def _connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)

    def _close(self):
        self.socket.close()
        self.context.term()

    def send(self, db_name, command, datas):
        self.socket.send_multipart([Message(db_name=db_name, command=command, data=datas)])
        return self.socket.recv_multipart()[0]
