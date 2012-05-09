#!/usr/bin/env python
#Copyright (c) 2011 Fabula Solutions. All rights reserved.
#Use of this source code is governed by a BSD-style license that can be
#found in the license.txt file.

# leveldb client
import zmq
import threading
import time
import ujson as json


class Client(object):
    def __init__(self, bind="127.0.0.1", port="4141", timeout=10*1000):
        self.bind = bind
        self.port = port
        self.host = "tcp://%s:%s" % (self.bind, self.port)
        self.timeout = timeout
        self.connect()

    def __del__(self):
        self.close()


    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)


    def close(self):
        self.socket.close()
        self.context.term()




class Elevator(Client):
    def Get(self, key):
        self.socket.send_multipart(['GET', json.dumps([key])])
        return self.socket.recv_multipart()[0]

    def Put(self, key, value):
        self.socket.send_multipart(['PUT', json.dumps([key, value])])
        return self.socket.recv_multipart()[0]

    def Delete(self, key):
        self.socket.send_multipart(['DELETE', json.dumps([key])])
        return self.socket.recv_multipart()[0]

    def Range(self, start=None, limit=None):
        self.socket.send_multipart(['RANGE', json.dumps([start, limit])])
        return json.loads(self.socket.recv_multipart()[0])


class WriteBatch(Client):
    def __init__(self, *args, **kwargs):
        # Generate a unique id, in order to keep
        # trace of it over server side for it's further
        # updates.
        self.uid = int(time.time())
        self.bid = "%s:%d" % ('batch', self.uid)
        super(WriteBatch, self).__init__(*args, **kwargs)

    def __del__(self):
        self.socket.send_multipart(['BCLEAR', json.dumps([self.bid])])
        return self.socket.recv_multipart()[0]

    def Put(self, key, value):
        self.socket.send_multipart(['BPUT', json.dumps([key, value, self.bid])])
        return self.socket.recv_multipart()[0]

    def Delete(self, key):
        self.socket.send_multipart(['BDELETE', json.dumps([key, self.bid])])
        return self.socket.recv_multipart()[0]

    def Write(self):
        self.socket.send_multipart(['BWRITE', json.dumps([self.bid])])
        return self.socket.recv_multipart()[0]
