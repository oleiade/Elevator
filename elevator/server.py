#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import traceback
import zmq
import logging
import procname

from elevator import conf
from elevator.env import Environment
from elevator.backend import WorkersPool
from elevator.frontend import Proxy
from elevator.utils.daemon import Daemon


ARGS = conf.init_parser().parse_args(sys.argv[1:])


def setup_process_name(env):
    args = env['args']
    endpoint = ' {0}://{1}:{2} '.format(args['protocol'],
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
        raise ValueError('Invalid log level: %s' % loglevel)
    
    activity_logger = logging.getLogger("activity_logger")
    activity_logger.setLevel(numeric_level)
    activity_stream = logging.FileHandler(activity_log_file)
    activity_formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(funcName)s : %(message)s")
    activity_stream.setFormatter(activity_formatter)
    activity_logger.addHandler(activity_stream)

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

    workers_pool = WorkersPool(args['workers'])
    proxy = Proxy('%s://%s:%s' % (args['protocol'], args['bind'], args['port']))

    poll = zmq.Poller()
    poll.register(workers_pool.socket, zmq.POLLIN)
    poll.register(proxy.socket, zmq.POLLIN)

    activity_logger.info('Elevator server started\n'
                         'Ready to accept '
                         'connections on port %s' % args['port'])

    while True:
        try:
            sockets = dict(poll.poll())
            if proxy.socket in sockets:
                if sockets[proxy.socket] == zmq.POLLIN:
                    msg = proxy.socket.recv_multipart(copy=False)
                    workers_pool.socket.send_multipart(msg, copy=False)

            if workers_pool.socket in sockets:
                if sockets[workers_pool.socket] == zmq.POLLIN:
                    msg = workers_pool.socket.recv_multipart(copy=False)
                    proxy.socket.send_multipart(msg, copy=False)
        except KeyboardInterrupt:
            activity_logger.info('Gracefully shuthing down workers')
            del workers_pool
            activity_logger.info('Stopping proxy')
            del proxy
            activity_logger.info('Done')
            sys.exit(0)
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
