from .base import Client


class WriteBatch(Client):
    def __init__(self, *args, **kwargs):
        self.container = {}
        super(WriteBatch, self).__init__(*args, **kwargs)

    def Put(self, key, value):
        self.container[key] = value

    def Delete(self, key):
        del self.container[key]

    def Write(self):
        return self.send(self.db_uid, 'BATCH', [self.container.items()])
