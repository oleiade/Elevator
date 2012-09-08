#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import zmq


from elevator import conf
from elevator.env import Environment
from elevator.backend import WorkersPool
from elevator.frontend import Proxy
from elevator.utils.daemon import Daemon


ARGS = conf.init_parser().parse_args(sys.argv[1:])


def runserver(env):
    args = ARGS

    workers_pool = WorkersPool(args.workers)
    proxy = Proxy('tcp://%s:%s' % (args.bind, args.port))

    poll = zmq.Poller()
    poll.register(workers_pool.socket, zmq.POLLIN)
    poll.register(proxy.socket, zmq.POLLIN)

    try:
        print >> sys.stdout, "Elevator server started"
        print >> sys.stdout, "The server is now ready to accept " \
                             "connections on port %s" % args.port
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
        del workers_pool
        del proxy


class ServerDaemon(Daemon):
    def run(self, env):
        super(self, Daemon).run()
        while True:
            runserver(env)


def main():
    # As Environment object is a singleton
    # every further instanciation of the object
    # will point on this one, and conf will be
    # present in it yet.
    env = Environment(ARGS.config)

    if ARGS.daemon:
        server_daemon = ServerDaemon('/tmp/elevator.pid')
        server_daemon.start()
    else:
        runserver(env)
