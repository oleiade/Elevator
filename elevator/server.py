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
from elevator.db import DatabasesHandler
from elevator.env import Environment
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


def setup_loggers(env):
    activity_log_file = env['global']['activity_log']
    errors_log_file = env['global']['errors_log']

    # Setup up activity logger
    numeric_level = getattr(logging, env['args']['log_level'].upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % env['args']['log_level'].upper())

    # Set up activity logger on file and stderr
    activity_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(funcName)s : %(message)s")
    file_stream = logging.FileHandler(activity_log_file)
    stderr_stream = logging.StreamHandler(sys.stdout)
    file_stream.setFormatter(activity_formatter)
    stderr_stream.setFormatter(activity_formatter)

    activity_logger = logging.getLogger("activity_logger")
    activity_logger.setLevel(numeric_level)
    activity_logger.addHandler(file_stream)
    activity_logger.addHandler(stderr_stream)

    # Setup up activity logger
    errors_logger = logging.getLogger("errors_logger")
    errors_logger.setLevel(logging.WARNING)
    errors_stream = logging.FileHandler(errors_log_file)
    errors_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(funcName)s : %(message)s")
    errors_stream.setFormatter(errors_formatter)
    errors_logger.addHandler(errors_stream)


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
    databases = DatabasesHandler(database_store, databases_storage)

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
        server_daemon = ServerDaemon('/tmp/elevator.pid')
        server_daemon.start()
    else:
        runserver(env)
