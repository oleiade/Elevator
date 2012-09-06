import ujson as json

from .base import Client


class Elevator(Client):
    def Get(self, key):
        self.socket.send_multipart([self.db_name, 'GET', json.dumps([key])])
        return self.socket.recv_multipart()[0]

    def Put(self, key, value):
        self.socket.send_multipart([self.db_name, 'PUT', json.dumps([key, value])])
        return self.socket.recv_multipart()[0]

    def Delete(self, key):
        self.socket.send_multipart([self.db_name, 'DELETE', json.dumps([key])])
        return self.socket.recv_multipart()[0]

    def Range(self, start=None, limit=None):
        self.socket.send_multipart([self.db_name, 'RANGE', json.dumps([start, limit])])
        return json.loads(self.socket.recv_multipart()[0])

    def ListDatabases(self):
        self.socket.send_multipart([self.db_name, 'DBLIST', json.dumps({})])
        return json.loads(self.socket.recv_multipart()[0])

    def CreateDatabase(self, key):
        self.socket.send_multipart([self.db_name, 'DBCREATE', json.dumps([key])])
        return json.loads(self.socket.recv_multipart()[0])
