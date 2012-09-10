import os
import uuid
import leveldb
import ujson as json


class DatabaseOptions(dict):
    def __init__(self, *args, **kwargs):
        self['create_if_missing'] = True
        self['error_if_exists'] = False
        self['paranoid_checks'] = False
        self['block_cache_size'] = 8 * (2 << 20)
        self['write_buffer_size'] = 2 * (2 << 20)
        self['block_size'] = 4096
        self['max_open_files'] = 1000

        for key, value in kwargs:
            if key in self:
                self[key] = value


class DatabasesHandler(dict):
    def __init__(self, store, dest, *args, **kwargs):
        self['index'] = {}
        self['reverse_index'] = {}
        self['paths_index'] = {}
        self.dest = dest
        self.store = store
        self.load()

    def load(self):
        try:
            store_datas = json.load(open(self.store, 'r'))
        except IOError:
            store_datas = {}

        for db_name, db_desc in store_datas.iteritems():
            self['index'].update({db_name: db_desc['uid']})
            self['reverse_index'].update({db_desc['uid']: db_name})
            self['paths_index'].update({db_desc['uid']: db_desc['path']})
            self.update({db_desc['uid']: leveldb.LevelDB(db_desc['path'])})

        # Always bootstrap 'default'
        if 'default' not in self['index']:
            self.add('default')

    def persist(self, db_name, db_desc):
        try:
            store_datas = json.load(open(self.store, 'r'))
        except IOError:
            store_datas = {}

        store_datas.update({db_name: db_desc})
        json.dump(store_datas, open(self.store, 'w'))

    def add(self, db_name, db_options=None):
        new_db_name = db_name
        new_db_desc = {
            'path': os.path.join(self.dest, new_db_name),
            'uid': str(uuid.uuid4()),
            'options': db_options if db_options is not None else DatabaseOptions(),
        }
        self.persist(new_db_name, new_db_desc)

        self['index'].update({new_db_name: new_db_desc['uid']})
        self['reverse_index'].update({new_db_desc['uid']: new_db_name})
        self['paths_index'].update({new_db_desc['uid']: new_db_desc['path']})
        self.update({new_db_desc['uid']: leveldb.LevelDB(new_db_desc['path'], **new_db_desc['options'])})

    def drop(self, db_name):
        db_uid = self['index'].pop(db_name)
        del self['db_uid']
        os.remove(os.path.join(self.dest, db_name))
        self.pop(db_uid)

    def list(self):
        return [db_name for db_name in self['index'].iterkeys()]
