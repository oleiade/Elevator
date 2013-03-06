import os
import zmq
import time
import shutil
import threading
import unittest2

from elevator.db import DatabaseStore
from elevator.backend.supervisor import Supervisor
from elevator.backend.worker import Worker
from elevator.backend.protocol import WORKER_STATUS

from ..fakers import gen_test_config


class SupervisorTest(unittest2.TestCase):
    def setUp(self):
        zmq_context = zmq.Context()
        config = gen_test_config()

        self.database_store = config['database_store']
        self.databases_storage_path = config['databases_storage_path']
        if not os.path.exists(self.databases_storage_path):
            os.mkdir(self.databases_storage_path)
        self.db_handler = DatabaseStore(config)

        # Let's fake a backend for workers to talk to
        self.socket = zmq_context.socket(zmq.DEALER)
        self.socket.bind('inproc://backend')

        self.supervisor = Supervisor(zmq_context, self.db_handler)

    def tearDown(self):
        self.supervisor.stop_all()
        os.remove(self.database_store)
        shutil.rmtree(self.databases_storage_path)

    def test_init_workers_with_positive_count(self):
        start_thread_count = len(threading.enumerate())
        workers_count = 4

        self.supervisor.init_workers(workers_count)
        time.sleep(1)  # Wait for workers to start

        self.assertEqual(len(threading.enumerate()),
                         start_thread_count + workers_count)
        self.assertEqual(len(self.supervisor.workers), workers_count)

        for _id, worker in self.supervisor.workers.iteritems():
            self.assertIn('thread', worker)
            self.assertIsInstance(worker['thread'], threading.Thread)
            self.assertTrue(worker['thread'].isAlive())

            self.assertIn('socket', worker)

    def test_stop_specific_worker(self):
        start_thread_count = len(threading.enumerate())
        workers_count = 4
        self.supervisor.init_workers(workers_count)
        time.sleep(1)  # Wait for the workers to start
        worker_to_stop = self.supervisor.workers.keys()[0]

        self.assertEqual(len(threading.enumerate()),
                         start_thread_count + workers_count)

        self.supervisor.stop(worker_to_stop)

        self.assertEqual(len(threading.enumerate()),
                         (start_thread_count + workers_count) - 1)
        self.assertNotIn(worker_to_stop, self.supervisor.workers)

    def test_stop_all(self):
        start_thread_count = len(threading.enumerate())
        workers_count = 4
        self.supervisor.init_workers(workers_count)
        time.sleep(1)  # Wait for the workers to start

        self.assertEqual(len(threading.enumerate()),
                         start_thread_count + workers_count)

        self.supervisor.stop_all()

        self.assertEqual(len(threading.enumerate()),
                         start_thread_count)
        self.assertEqual(len(self.supervisor.workers), 0)

    def test_specific_worker_status(self):
        workers_count = 4
        self.supervisor.init_workers(workers_count)
        worker_to_ask = self.supervisor.workers.keys()[0]

        status = self.supervisor.status(worker_to_ask)
        self.assertIsInstance(status, list)
        self.assertEqual(len(status), 1)
        self.assertEqual(status[0], (str(Worker.STATES.IDLE),))

    def test_workers_status(self):
        workers_count = 4
        self.supervisor.init_workers(workers_count)

        status = self.supervisor.statuses()
        self.assertIsInstance(status, list)
        self.assertEqual(len(status), 4)
        self.assertEqual(status, [(str(Worker.STATES.IDLE),)] * 4)

    def test_inactive_worker_last_activity(self):
        workers_count = 2
        self.supervisor.init_workers(workers_count)
        worker_to_ask = self.supervisor.workers.keys()[0]

        status = self.supervisor.last_activity(worker_to_ask)
        self.assertIsInstance(status, list)
        self.assertEqual(len(status), 1)
        self.assertEqual(status[0], (None, None))

    def test_inactive_workers_last_activities(self):
        workers_count = 2
        self.supervisor.init_workers(workers_count)

        status = self.supervisor.last_activity_all()
        self.assertIsInstance(status, list)
        self.assertEqual(len(status), 2)
        self.assertEqual(status[0], (None, None))
        self.assertEqual(status[1], (None, None))

    def test_valid_working_command_with_workers(self):
        workers_count = 4
        self.supervisor.init_workers(workers_count)

        responses = self.supervisor.command(WORKER_STATUS,
                                            max_retries=1,
                                            timeout=100)

        self.assertIsInstance(responses, list)
        self.assertGreaterEqual(len(responses), 4)

    def test_valid_working_command_without_workers(self):
        responses = self.supervisor.command(WORKER_STATUS,
                                            max_retries=1,
                                            timeout=100)

        self.assertIsInstance(responses, list)
        self.assertEqual(responses, [])

    def test_invalid_command_with_workers(self):
        workers_count = 2
        self.supervisor.init_workers(workers_count)

        responses = self.supervisor.command("NONEXISTINGCOMMAND",
                                            max_retries=1,
                                            timeout=100)

        self.assertIsInstance(responses, list)
        self.assertEqual(responses, [])

