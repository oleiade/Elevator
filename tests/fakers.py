import os
import shutil
import subprocess
import tempfile
import ConfigParser

from elevator.env import Environment


def gen_test_env():
    tmp = tempfile.mkdtemp(dir='/tmp')
    return Environment(**{
        'global': {
            'daemonize': 'no',
            'pidfile': os.path.join(tmp, 'elevator_test.pid'),
            'databases_storage_path': os.path.join(tmp, 'elevator_test'),
            'database_store': os.path.join(tmp, 'elevator_test/store.json'),
            'default_db': 'default',
            'port': 4141,
            'bind': '127.0.0.1',
            'activity_log': os.path.join(tmp, 'elevator_test.log'),
            'errors_log': os.path.join(tmp, 'elevator_errors.log'),
            'max_cache_size': 1024,
        }
    })


class TestDaemon(object):
    CONFIG_DICT = {
            "pidfile": "/tmp/elevator_test.pid",
            "databases_storage_path": "",  # Will be randomly set later
            "database_store": "/tmp/elevator_store.json",
            "port": "60000",
            "activity_log": "/tmp/elevator_test.log",
            "errors_log": "/tmp/elevator_errors_test.log",
    }
    FILES_TO_COLLECT = [
        CONFIG_DICT['pidfile'],
        CONFIG_DICT['database_store'],
        CONFIG_DICT['activity_log'],
        CONFIG_DICT['errors_log'],
    ]
    DIRS_TO_COLLECT = [
        CONFIG_DICT['databases_storage_path']
    ]

    def __init__(self):
        self.bootstrap_conf()
        self.process = None

        self.port = self.CONFIG_DICT['port']

    def __del__(self):
        # Remove every generated test files
        for f in self.FILES_TO_COLLECT:
            if os.path.exists(f):
                os.remove(f)

        # Remove every generated test dirs
        for d in self.DIRS_TO_COLLECT:
            if os.path.exists(d):
                shutil.rmtree(d)

        os.remove(self.conf_file)

    def bootstrap_conf(self):
        self.conf_file = '/tmp/elevator_test.conf'
        conf_file = open(self.conf_file, 'a')

        config = ConfigParser.RawConfigParser()
        config.add_section('global')

        # Generate by hand the temporary databases storage path
        self.CONFIG_DICT["databases_storage_path"] = tempfile.mkdtemp(dir='/tmp')
        for option, value in self.CONFIG_DICT.iteritems():
            config.set('global', option, value)

        config.write(conf_file)

    def start(self):
        self.process = subprocess.Popen(['elevator',
                                         '--config', self.conf_file,
                                         '--port', self.port])

    def stop(self):
        self.process.kill()