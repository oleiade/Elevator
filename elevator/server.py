# -*- coding:utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import sys
import traceback
import zmq
import logging
import procname

from elevator import args
from elevator.db import DatabaseStore
from elevator.env import Environment
from elevator.log import setup_loggers
from elevator.backend import Backend
from elevator.frontend import Frontend
from elevator.utils.daemon import Daemon


ARGS = args.init_parser().parse_args(sys.argv[1:])


def setup_process_name(env):
    args = env['args']
    endpoint = ' {0}://{1}:{2} '.format(args['transport'],
                                        args['bind'],
                                        args['port'])
    config = ' --config {0} '.format(args['config'])
    process_name = 'elevator' + endpoint + config

    procname.setprocname(process_name)


def log_uncaught_exceptions(e, paranoid=False):
    errors_logger = logging.getLogger("errors_logger")
    tb = traceback.format_exc()

    # Log into errors log
    errors_logger.critical(''.join(tb))
    errors_logger.critical('{0}: {1}'.format(type(e), e.message))

    # Log into stderr
    logging.critical(''.join(tb))
    logging.critical('{0}: {1}'.format(type(e), e.message))

    if paranoid:
        sys.exit(1)


def runserver(env):
    args = env['args']
    setup_loggers(env)
    activity_logger = logging.getLogger("activity_logger")

    database_store = env['global']['database_store']
    databases_storage = env['global']['databases_storage_path']
    databases = DatabaseStore(database_store, databases_storage)

    backend = Backend(databases, args['workers'])
    frontend = Frontend(args['transport'], ':'.join([args['bind'], args['port']]))

    poller = zmq.Poller()
    poller.register(backend.socket, zmq.POLLIN)
    poller.register(frontend.socket, zmq.POLLIN)

    activity_logger.info('Elevator server started on %s' % frontend.host)

    while True:
        try:
            sockets = dict(poller.poll())
            if frontend.socket in sockets:
                if sockets[frontend.socket] == zmq.POLLIN:
                    msg = frontend.socket.recv_multipart(copy=False)
                    backend.socket.send_multipart(msg, copy=False)

            if backend.socket in sockets:
                if sockets[backend.socket] == zmq.POLLIN:
                    msg = backend.socket.recv_multipart(copy=False)
                    frontend.socket.send_multipart(msg, copy=False)
        except KeyboardInterrupt:
            activity_logger.info('Gracefully shuthing down workers')
            del backend
            activity_logger.info('Stopping frontend')
            del frontend
            activity_logger.info('Done')
            return
        except Exception as e:
            log_uncaught_exceptions(e, paranoid=args['paranoid'])


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
    env.load_from_args('args', ARGS._get_kwargs())
    setup_process_name(env)

    if env['args']['daemon'] is True:
        server_daemon = ServerDaemon('/var/run/elevator.pid')
        server_daemon.start()
    else:
        runserver(env)
