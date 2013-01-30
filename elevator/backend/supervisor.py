# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq

from collections import defaultdict

from elevator.utils.snippets import sec_to_ms
from elevator.constants import WORKER_HALT, WORKER_STATUS

from elevator.backend.worker import Worker


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
        self.socket.bind('inproc://remote')

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
                self.socket.send_multipart([self.workers[worker_id]['socket'], instruction], flags=zmq.NOBLOCK)

                retried = 0
                while retried <= max_retries:
                    sockets = dict(self.poller.poll(self.timeout))

                    if sockets:
                        if sockets.get(self.socket) == zmq.POLLIN:
                            responses.append(self.socket.recv_multipart(flags=zmq.NOBLOCK)[1])
                            break
                    else:
                        retried += 1

                if retried == max_retries:
                    err_msg = "Instruction %s sent to %s failed. Retried %d times"
                    errors_logger.error(err_msg % (instruction, worker_id, retried))

        return responses

    def statuses(self):
        return self.command(WORKER_STATUS)

    def stop(self, worker_id):
        return self.command(WORKER_HALT, [worker_id])

    def stop_all(self):
        return self.command(WORKER_HALT)

    def init_workers(self, count):
        pos = 0

        while pos < count:
            # Start a worker
            worker = Worker(self.zmq_context, self.databases_store)
            worker.start()
            socket_id, worker_id = self.socket.recv_multipart()
            self.workers[worker_id]['socket'] = socket_id
            self.workers[worker_id]['thread'] = worker
            pos += 1
