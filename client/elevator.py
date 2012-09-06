from .base import Client


class Elevator(Client):
    def Get(self, key):
        return self.send(self.db_name, 'GET', [key])

    def Put(self, key, value):
        return self.send(self.db_name, 'PUT', [key, value])

    def Delete(self, key):
        return self.send(self.db_name, 'DELETE', [key])

    def Range(self, start=None, limit=None):
        return self.send(self.db_name, 'RANGE', [start, limit])

    def ListDatabases(self):
        return self.send(self.db_name, 'DBLIST', {})

    def CreateDatabase(self, key):
        return self.send(self.db_name, 'DBCREATE', [key])
