import os
import md5
import leveldb
import types


class DatabaseOptions(dict):
    def __init__(self, *args, **kwargs):
        self['create_if_missing'] =  True
        self['error_if_exists'] = False
        self['paranoid_checks'] = False
        self['block_cache_size'] =  8 * (2 << 20)
        self['write_buffer_size'] = 2 * (2 << 20)
        self['block_size'] = 4096
        self['max_open_files'] = 1000

        for key, value in kwargs:
            if key in self:
                self[key] = value

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

    def add(self, db_name, db_options=None):
        new_db_name = db_name
        new_db_uid = md5.new(new_db_name).digest()
        new_db_dest = os.path.join(self.dest, new_db_name)
        new_db_options = db_options if db_options is not None else DatabaseOptions()

        self['index'].update({new_db_name: new_db_uid})
        self.update({new_db_uid: leveldb.LevelDB(new_db_dest, **new_db_options)})

    def drop(self, db_name):
        db_uid = self['index'].pop(db_name)
        del self['db_uid']
        os.remove(os.path.join(self.dest, db_name))
        self.pop(db_uid)

    def list(self):
        return [db_name for db_name in self['index'].iterkeys()]
