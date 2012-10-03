import os
import shutil
import subprocess
import tempfile
import ConfigParser
import tempfile
import random

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


def gen_test_conf():
    """Generates a ConfigParser object built with test options values"""
    global_config_options = {
            "pidfile": tempfile.mkstemp(suffix=".pid", dir='/tmp')[1],
            "databases_storage_path": tempfile.mkdtemp(dir='/tmp'),  # Will be randomly set later
            "database_store": tempfile.mkstemp(suffix=".json", dir="/tmp")[1],
            "port": str(random.randint(4142, 60000)),
            "activity_log": tempfile.mkstemp(suffix=".log", dir="/tmp")[1],
            "errors_log": tempfile.mkstemp(suffix="_errors.log", dir="/tmp")[1],
    }
    config = ConfigParser.ConfigParser()
    config.add_section('global')

    for key, value in global_config_options.iteritems():
        config.set('global', key, value)

    return config


class TestDaemon(object):
    def __init__(self):
        self.bootstrap_conf()
        self.process = None

        self.port = self.config.get('global', 'port')

    def __del__(self):
        for key, value in self.config.items('global'):
            if os.path.exists(value):
                if os.path.isfile(value):
                    os.remove(value)
                elif os.path.isdir(value):
                    shutil.rmtree(value)

        self.conf_file.close()
        os.remove(self.conf_file_path)

    def bootstrap_conf(self):
        self.conf_file_path = '/tmp/elevator_test.conf'
        self.config = gen_test_conf()
        self.conf_file = open(self.conf_file_path, 'a')
        self.config.write(self.conf_file)

    def start(self):
        self.process = subprocess.Popen(['elevator',
                                         '--config', self.conf_file,
                                         '--port', self.port])

    def stop(self):
        self.process.kill()
