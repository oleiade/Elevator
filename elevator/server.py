#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, time
import zmq
import leveldb
import threading

import conf

from database import Backend, Frontend
from utils.daemon import Daemon


class ServerDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)


def run():
    args = conf.init_parser().parse_args(sys.argv[1:])

    backend = Backend(args.db)
    frontend = Frontend('tcp://%s:%s' % (args.bind, args.port))

    poll = zmq.Poller()
    poll.register(backend.socket, zmq.POLLIN)
    poll.register(frontend.socket, zmq.POLLIN)

    try:
        print >> sys.stdout, "Elevator server started"
        print >> sys.stdout, "The server is now ready to accept connections on port %s" % args.port
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
