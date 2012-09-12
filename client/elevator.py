from .base import Client



class Elevator(Client):
    def Get(self, key):
        return self.send(self.db_uid, 'GET', [key])

    def BGet(self, keys):
        return self.send(self.db_uid, 'BGET', [keys])

    def Put(self, key, value):
        return self.send(self.db_uid, 'PUT', [key, value])

    def Delete(self, key):
        return self.send(self.db_uid, 'DELETE', [key])

    def Range(self, start=None, limit=None):
        return self.send(self.db_uid, 'RANGE', [start, limit])

