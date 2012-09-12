from __future__ import absolute_import

import zmq
import msgpack
import lz4

from .message import Message, MessageOptions
from .error import ELEVATOR_ERROR

from elevator.constants import FAILURE_STATUS

from elevator.db import DatabaseOptions


class Client(object):
    def __init__(self, db_name='default', *args, **kwargs):
        self.bind = kwargs.pop('bind', '127.0.0.1')
        self.port = kwargs.pop('port', '4141')
        self._db_uid = None
        self.timeout = kwargs.pop('timeout', 10 * 10000)
        self.host = "tcp://%s:%s" % (self.bind, self.port)

        self._connect(db_name=db_name)

    def __del__(self):
        self._close()

    def _connect(self, db_name):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)
        self.connect(db_name)

    def _close(self):
        self.socket.close()
        self.context.term()

    def connect(self, db_name):
        self.db_uid = self.send(db_name, 'DBCONNECT', {'db_name': db_name})
        self.db_name = db_name
        return

    def listdb(self):
        return self.send(self.db_uid, 'DBLIST', {})

    def createdb(self, key, db_options=None):
        db_options = db_options if not None else DatabaseOptions()
        return self.send(self.db_uid, 'DBCREATE', [key, db_options])

    def dropdb(self, key):
        return self.send(self.db_uid, 'DBDROP', [key])

    def repairdb(self):
        return self.send(self.db_uid, 'DBREPAIR', {})

    def send(self, db_uid, command, datas):
        msg_options = MessageOptions(compressed=True)
        msg = Message(db_uid=db_uid, command=command, data=datas, compression=lz4.dumps)
        import sys
        print sys.getsizeof(msg), len(msg)
        self.socket.send_multipart([msg_options, msg])
        status, content = msgpack.unpackb(self.socket.recv_multipart()[0])

        if status == FAILURE_STATUS:
            error_code, error_msg = content
            raise ELEVATOR_ERROR[error_code](error_msg)
        return content
