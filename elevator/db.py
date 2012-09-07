import os
import md5
import leveldb


class DatabasesHandler(dict):
    def __init__(self, dest, *args, **kwargs):
        self['index'] = {}
        self.dest = dest
        self._init_default_db()

    def _init_default_db(self):
        self.add('default')

    def load(self):
        # Retrieving every databases from database store on fs,
        # and adding them to backend databases handler.
        for db_name in os.lisdtir(self.store_path):
            if db_name != 'default':
                db_path = os.path.join(self.store_path, db_name)
                db_uid = md5.new(db_name).digest()
                self['index'].update({db_name: db_uid})
                self.update({db_uid: leveldb.LevelDB(db_path)})

    def add(self, db_name):
        new_db_name = db_name
        new_db_uid = md5.new(new_db_name).digest()
        new_db_dest = os.path.join(self.dest, new_db_name)

        self['index'].update({new_db_name: new_db_uid})
        self.update({new_db_uid: leveldb.LevelDB(new_db_dest)})

    def drop(self, db_name):
        db_uid = self['index'].pop(db_name)
        del self['db_uid']
        os.remove(os.path.join(self.dest, db_name))
        self.pop(db_uid)

    def list(self):
        return [db_name for db_name in self['index'].iterkeys()]
