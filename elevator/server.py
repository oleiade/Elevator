#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zmq
import leveldb
import threading

from database import Backend, Frontend


def run():
    backend = Backend('test')
    frontend = Frontend('tcp://127.0.0.1:4141')

    poll = zmq.Poller()
    poll.register(backend.socket, zmq.POLLIN)
    poll.register(frontend.socket, zmq.POLLIN)

    try:
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
