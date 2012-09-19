#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import zmq
import logging


from elevator import conf
from elevator.env import Environment
from elevator.backend import WorkersPool
from elevator.frontend import Proxy
from elevator.utils.daemon import Daemon


ARGS = conf.init_parser().parse_args(sys.argv[1:])


def setup_loggers(activity_file, errors_file):
    # Setup up activity logger
    activity_logger = logging.getLogger("activity_logger")
    activity_logger.setLevel(logging.DEBUG)
    activity_stream = logging.FileHandler(activity_file)
    activity_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(funcName)s : %(message)s")
    activity_stream.setFormatter(activity_formatter)
    activity_logger.addHandler(activity_stream)

    # Setup up activity logger
    errors_logger = logging.getLogger("errors_logger")
    errors_logger.setLevel(logging.WARNING)
    errors_stream = logging.FileHandler(errors_file)
    errors_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(funcName)s : %(message)s")
    errors_stream.setFormatter(errors_formatter)
    errors_logger.addHandler(errors_stream)


def runserver(env):
    args = ARGS

    activity_log = env['global'].pop('activity_log', '/var/log/elevator.log')
    errors_log = env['global'].pop('errors_log', '/var/log/elevator_errors.log')
    setup_loggers(activity_log,
                  errors_log)
    activity_logger = logging.getLogger("activity_logger")

    workers_pool = WorkersPool(args.workers)
    proxy = Proxy('%s://%s:%s' % (args.protocol, args.bind, args.port))

    poll = zmq.Poller()
    poll.register(workers_pool.socket, zmq.POLLIN)
    poll.register(proxy.socket, zmq.POLLIN)

    try:
        activity_logger.info('Elevator server started\n'
               'Ready to accept '
               'connections on port %s' % args.port)

        while True:
            sockets = dict(poll.poll())
            if proxy.socket in sockets:
                if sockets[proxy.socket] == zmq.POLLIN:
                    msg = proxy.socket.recv_multipart()
                    workers_pool.socket.send_multipart(msg)

            if workers_pool.socket in sockets:
                if sockets[workers_pool.socket] == zmq.POLLIN:
                    msg = workers_pool.socket.recv_multipart()
                    proxy.socket.send_multipart(msg)
    except KeyboardInterrupt:
        activity_logger.info('Gracefully shuthing down workers')
        del workers_pool
        activity_logger.info('Stopping proxy')
        del proxy
    activity_logger.info('Done')


class ServerDaemon(Daemon):
    def run(self):
        env = Environment()  # Already bootstraped singleton obj
        while True:
            runserver(env)


def main():
    # As Environment object is a singleton
    # every further instanciation of the object
    # will point on this one, and conf will be
    # present in it yet.
    env = Environment(ARGS.config)

    if ARGS.daemon:
        server_daemon = ServerDaemon('/var/run/elevator.pid', stderr=None)
        server_daemon.start()
    else:
        runserver(env)
