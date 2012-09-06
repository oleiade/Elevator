import uuid
import ujson as json

from .base import Client


class WriteBatch(Client):
    def __init__(self, *args, **kwargs):
        # Generate a unique id, in order to keep
        # trace of it over server side for it's further
        # updates.
        self.uid = str(uuid.uuid4())
        self.bid = "%s:%s" % ('batch', self.uid)
        super(WriteBatch, self).__init__(*args, **kwargs)

    def __del__(self):
        self.socket.send_multipart([self.db_name, 'BCLEAR', json.dumps([self.bid])])
        return self.socket.recv_multipart()[0]

    def Put(self, key, value):
        self.socket.send_multipart([self.db_name, 'BPUT', json.dumps([key, value, self.bid])])
        return self.socket.recv_multipart()[0]

    def Delete(self, key):
        self.socket.send_multipart([self.db_name, 'BDELETE', json.dumps([key, self.bid])])
        return self.socket.recv_multipart()[0]

    def Write(self):
        self.socket.send_multipart([self.db_name, 'BWRITE', json.dumps([self.bid])])
        return self.socket.recv_multipart()[0]
