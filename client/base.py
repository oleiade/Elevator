import zmq
import msgpack

from .message import Message


class Client(object):
    def __init__(self, *args, **kwargs):
        self.bind = kwargs.pop('bind', '127.0.0.1')
        self.port = kwargs.pop('port', '4141')
        self.db_uid = None
        self.timeout = kwargs.pop('timeout', 10 * 10000)
        self.host = "tcp://%s:%s" % (self.bind, self.port)
        self._connect()

    def __del__(self):
        self._close()

    def _connect(self, db_name='default'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)
        self.connect(db_name)

    def _close(self):
        self.socket.close()
        self.context.term()

    def connect(self, db_name):
        self.db_uid = self.send(db_name, 'DBCONNECT', {'db_name': db_name})
        return

    def listdb(self):
        return self.send(self.db_uid, 'DBLIST', {})

    def createdb(self, key):
        return self.send(self.db_uid, 'DBCREATE', [key])

    def send(self, db_uid, command, datas):
        self.socket.send_multipart([Message(db_uid=db_uid, command=command, data=datas)])
        return msgpack.unpackb(self.socket.recv_multipart()[0])
