import os
import uuid
import leveldb
import ujson as json

from shutil import rmtree

from .constants import FAILURE_STATUS, SUCCESS_STATUS,\
                       OS_ERROR, KEY_ERROR


class DatabaseOptions(dict):
    def __init__(self, *args, **kwargs):
        self['create_if_missing'] = True
        self['error_if_exists'] = False
        self['paranoid_checks'] = False
        self['block_cache_size'] = 8 * (2 << 20)
        self['write_buffer_size'] = 2 * (2 << 20)
        self['block_size'] = 4096
        self['max_open_files'] = 1000

        for key, value in kwargs.iteritems():
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

    def extract_store_datas(self):
        try:
            store_datas = json.load(open(self.store, 'r'))
        except IOError:
            store_datas = {}

        return store_datas

    def load(self):
        store_datas = self.extract_store_datas()

        for db_name, db_desc in store_datas.iteritems():
            self['index'].update({db_name: db_desc['uid']})
            self['reverse_index'].update({db_desc['uid']: db_name})
            self['paths_index'].update({db_desc['uid']: db_desc['path']})
            self.update({db_desc['uid']: leveldb.LevelDB(db_desc['path'])})

        # Always bootstrap 'default'
        if 'default' not in self['index']:
            self.add('default')

    def store_update(self, db_name, db_desc):
        store_datas = self.extract_store_datas()

        store_datas.update({db_name: db_desc})
        json.dump(store_datas, open(self.store, 'w'))

    def store_remove(self, db_name):
        store_datas = self.extract_store_datas()
        store_datas.pop(db_name)
        json.dump(store_datas, open(self.store, 'w'))

    def add(self, db_name, db_options=None):
        db_options = DatabaseOptions(db_options) or DatabaseOptions
        db_name_is_path = db_name.startswith('.') or ('/' in db_name)
        is_abspath = lambda: not db_name.startswith('.') and ('/' in db_name)

        # if db_name is a full path too, use it as name and path
        # in the same time
        if db_name_is_path:
            if not is_abspath():
                return (FAILURE_STATUS,
                        [KEY_ERROR, "Canno't create database from relative path"])
            try:
                new_db_path = db_name
                if not os.path.exists(new_db_path):
                    os.mkdir(new_db_path)
            except OSError as e:
                return (FAILURE_STATUS,
                        [OS_ERROR, e.strerror])
        else:
            new_db_path = os.path.join(self.dest, db_name)

        path = new_db_path
        uid = str(uuid.uuid4())
        options = db_options
        self.store_update(db_name, {
            'path': path,
            'uid': uid,
            'options': options,
        })

        self['index'].update({db_name: uid})
        self['reverse_index'].update({uid: db_name})
        self['paths_index'].update({uid: path})
        self.update({uid: leveldb.LevelDB(path, **options)})

        return SUCCESS_STATUS, None

    def drop(self, db_name):
        db_uid = self['index'].pop(db_name)
        db_path = self['paths_index'][db_uid]

        self['reverse_index'].pop(db_uid)
        self['paths_index'].pop(db_uid)
        self.pop(db_uid)
        self.store_remove(db_name)

        try:
            rmtree(db_path)
        except OSError:
            pass

        return SUCCESS_STATUS, None

    def exists(self, db_name):
        db_uid = self['index'][db_name] if db_name in self['index'] else None

        if db_uid:
            if os.path.exists(self['paths_index'][db_uid]):
                return True
            else:
                self.drop(db_name)

        return False

    def list(self):
        return [db_name for db_name
                in [key for key
                    in self['index'].iterkeys()]
                if self.exists(db_name)]
