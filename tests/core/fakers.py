# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import os
import shutil
import subprocess
import tempfile
import ConfigParser
import random

from elevator.env import Environment

mkdtemp = lambda _dir: tempfile.mkdtemp(suffix='-test',
                                        prefix='elevator-',
                                        dir=_dir)
mkstemp = lambda suffix, _dir: tempfile.mkstemp(suffix="-test" + suffix,
                                                prefix='elevator-',
                                                dir=_dir)[1]


def gen_test_env():
    tmp = mkdtemp('/tmp')
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
            "pidfile": mkstemp('.pid', '/tmp'),
            "databases_storage_path": mkdtemp('/tmp'),  # Will be randomly set later
            "database_store": mkstemp('.json', '/tmp'),
            "port": str(random.randint(4142, 60000)),
            "activity_log": mkstemp('.log', '/tmp'),
            "errors_log": mkstemp('_errors.log', '/tmp'),
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
            if not isinstance(value, (int, float)) and os.path.exists(value):
                if os.path.isfile(value):
                    os.remove(value)
                elif os.path.isdir(value):
                    shutil.rmtree(value)

        os.remove(self.conf_file_path)

    def bootstrap_conf(self):
        self.conf_file_path = mkstemp('.conf', '/tmp')
        self.config = gen_test_conf()

        with open(self.conf_file_path) as f:
            self.config.write(f)

    def start(self):
        self.process = subprocess.Popen(['elevator',
                                         '--config', self.conf_file_path,
                                         '--port', self.port])

    def stop(self):
        self.process.kill()
