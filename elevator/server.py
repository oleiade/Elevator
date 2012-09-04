#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import zmq


from elevator import conf
from elevator.env import Environment
from elevator.proxy import Backend, Frontend
from elevator.utils.daemon import Daemon


ARGS = conf.init_parser().parse_args(sys.argv[1:])


def runserver(env):
    args = ARGS

    backend = Backend(args.db)
    frontend = Frontend('tcp://%s:%s' % (args.bind, args.port))

    poll = zmq.Poller()
    poll.register(backend.socket, zmq.POLLIN)
    poll.register(frontend.socket, zmq.POLLIN)

    try:
        print >> sys.stdout, "Elevator server started"
        print >> sys.stdout, "The server is now ready to accept " \
                             "connections on port %s" % args.port
        while True:
            sockets = dict(poll.poll())
            if frontend.socket in sockets:
                if sockets[frontend.socket] == zmq.POLLIN:
                    msg = frontend.socket.recv_multipart()
                    backend.socket.send_multipart(msg)

            if backend.socket in sockets:
                if sockets[backend.socket] == zmq.POLLIN:
                    msg = backend.socket.recv_multipart()
                    frontend.socket.send_multipart(msg)
    except KeyboardInterrupt:
        del backend
        del frontend


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
