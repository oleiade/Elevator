import os
import zmq
import shutil
import unittest2

from elevator.db import DatabaseStore
from elevator.backend.atm import Majordome
from elevator.backend.supervisor import Supervisor

from ..fakers import gen_test_env


class MajordomeTest(unittest2.TestCase):
    def setUp(self):
        zmq_context = zmq.Context()
        env = gen_test_env()

        self.database_store = env['global']['database_store']
        self.databases_storage_path = env['global']['databases_storage_path']

        if not os.path.exists(self.databases_storage_path):
            os.mkdir(self.databases_storage_path)

        self.db_handler = DatabaseStore(self.database_store,
                                           self.databases_storage_path)

        # Let's fake a backend for workers to talk to
        self.socket = zmq_context.socket(zmq.DEALER)
        self.socket.bind('inproc://backend')

        self.supervisor = Supervisor(zmq_context, self.db_handler)

    def tearDown(self):
        self.supervisor.stop_all()

        if hasattr(self, 'majordome'):
            self.majordome.cancel()

        os.remove(self.database_store)
        shutil.rmtree(self.databases_storage_path)

    def test_unmount_existing_mounted_database(self):
        default_db_uid = self.db_handler.index['name_to_uid']['default']
        db_to_watch = self.db_handler[default_db_uid]
        self.assertEqual(db_to_watch.status, DatabaseStore.STATUSES.MOUNTED)

        # Use 1/60 interval in order to set it as 1sec
        self.majordome = Majordome(self.supervisor,
                                   self.db_handler,
                                   1 / 60)
        self.assertEqual(db_to_watch.status, DatabaseStore.STATUSES.MOUNTED)

    def test_unmount_existing_unmounted_database(self):
        default_db_uid = self.db_handler.index['name_to_uid']['default']
        db_to_watch = self.db_handler[default_db_uid]

        self.assertEqual(db_to_watch.status, DatabaseStore.STATUSES.MOUNTED)
        self.db_handler.umount('default')
        self.assertEqual(db_to_watch.status, DatabaseStore.STATUSES.UNMOUNTED)

        # Use 1/60 interval in order to set it as 1sec
        self.majordome = Majordome(self.supervisor,
                                   self.db_handler,
                                   1 / 60)
        self.assertEqual(db_to_watch.status, DatabaseStore.STATUSES.UNMOUNTED)
