# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq
import logging

from collections import defaultdict

from elevator.utils.snippets import sec_to_ms

from elevator.backend.worker import Worker
from elevator.backend.protocol import ServiceMessage
from elevator.backend.protocol import WORKER_HALT, WORKER_STATUS


activity_logger = logging.getLogger("activity_logger")
errors_logger = logging.getLogger("errors_logger")


class Supervisor(object):
    """A remote control to lead them all

    Exposes an internal api to talk to database workers and
    give them orders.
    """
    def __init__(self, zmq_context, databases_store, timeout=3):
        self.databases_store = databases_store
        self.workers = defaultdict(dict)
        self.timeout = sec_to_ms(timeout)

        self.zmq_context = zmq_context
        self.socket = zmq_context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.bind('inproc://supervisor')

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def __del__(self):
        for worker_id, worker in self.workers.iteritems():
            self.stop(worker_id)
            worker['thread'].join()

    def command(self, instruction, workers_ids=None):
        """Command an action to workers.

        An optional list of workers ids can be provided
        as an argument, in order to restrain the command
        to specific workers.
        """
        workers_ids = workers_ids or self.workers.iterkeys()
        max_retries = 3
        responses = []

        for worker_id in workers_ids:
            if worker_id in self.workers:
                worker_socket = self.workers[worker_id]['socket']
                request = ServiceMessage.dumps(instruction)
                self.socket.send_multipart([worker_socket, request], flags=zmq.NOBLOCK)

                retried = 0
                while retried <= max_retries:
                    sockets = dict(self.poller.poll(self.timeout))

                    if sockets and sockets.get(self.socket) == zmq.POLLIN:
                        serialized_response = self.socket.recv_multipart(flags=zmq.NOBLOCK)[1]
                        responses.append(ServiceMessage.loads(serialized_response))
                        break
                    else:
                        retried += 1

                if retried == max_retries:
                    err_msg = "Instruction %s sent to %s failed. Retried %d times"
                    errors_logger.error(err_msg % (instruction, worker_id, retried))

        return responses

    def statuses(self):
        """Fetch workers statuses"""
        return self.command(WORKER_STATUS)

    def stop(self, worker_id):
        """Stop a specific worker"""
        return self.command(WORKER_HALT, [worker_id])

    def stop_all(self):
        """Stop every supervised workers"""
        return self.command(WORKER_HALT)

    def init_workers(self, count):
        """Starts `count` workers.

        Awaits for their id to be received (blocking), and
        registers their socket id and thread reference
        """
        pos = 0

        while pos < count:
            # Start a worker
            worker = Worker(self.zmq_context, self.databases_store)
            worker.start()

            socket_id, response = self.socket.recv_multipart()
            worker_id = ServiceMessage.loads(response)[0]

            self.workers[worker_id]['socket'] = socket_id
            self.workers[worker_id]['thread'] = worker
            pos += 1
