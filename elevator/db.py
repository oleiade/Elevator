import os
import uuid
import leveldb
import ujson as json

from shutil import rmtree

from .env import Environment
from .constants import FAILURE_STATUS, SUCCESS_STATUS,\
                       OS_ERROR, KEY_ERROR, RUNTIME_ERROR,\
                       DATABASE_ERROR
from .utils.snippets import from_bytes_to_mo


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
        self.env = Environment()
        self['index'] = {}
        self['reverse_index'] = {}
        self['paths_index'] = {}
        self.dest = dest
        self.store = store

        self._global_cache_size = None

        self.load()

    @property
    def global_cache_size(self):
        store_datas = self.extract_store_datas()
        max_caches = [int(db["options"]["block_cache_size"]) for db
                      in store_datas.itervalues()]

        return sum([from_bytes_to_mo(x) for x in max_caches])

    def _disposable_cache(self, new_cache_size):
        next_cache_size = self.global_cache_size + from_bytes_to_mo(new_cache_size)
        ratio = int(self.env["global"]["max_cache_size"]) - next_cache_size

        # Both values are in
        if ratio < 0:
            return (False, ratio)
        return (True, ratio)

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
        db_options = db_options or DatabaseOptions()
        cache_status, ratio = self._disposable_cache(db_options["block_cache_size"])
        if not cache_status:
            return (FAILURE_STATUS,
                    [DATABASE_ERROR,
                     "Not enough disposable cache memory "
                     "%d Mo missing" % ratio])

        db_name_is_path = db_name.startswith('.') or ('/' in db_name)
        is_abspath = lambda: not db_name.startswith('.') and ('/' in db_name)

        # Handle case when a db is a path
        if db_name_is_path:
            if not is_abspath():
                return (FAILURE_STATUS,
                        [DATABASE_ERROR, "Canno't create database from relative path"])
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
            return (FAILURE_STATUS,
                    [DATABASE_ERROR,
                    "Cannot drop db : %s, files not found"])

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
