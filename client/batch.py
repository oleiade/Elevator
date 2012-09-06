import uuid

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
        return self.send(self.db_uid, 'BCLEAR', [self.bid])

    def Put(self, key, value):
        return self.send(self.db_uid, 'BPUT', [key, value, self.bid])

    def Delete(self, key):
        return self.send(self.db_uid, 'BDELETE', [key, self.bid])

    def Write(self):
        return self.send(self.db_uid, 'BWRITE', [self.bid])
