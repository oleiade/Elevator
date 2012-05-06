#!/usr/bin/env python
#Copyright (c) 2011 Fabula Solutions. All rights reserved.
#Use of this source code is governed by a BSD-style license that can be
#found in the license.txt file.

# leveldb client
import zmq
import threading
import time
import ujson as json

class Elevator(object):
    def __init__(self, host="tcp://127.0.0.1:4141", timeout=10*1000):
        self.host = host
        self.timeout = timeout
        self.connect()


    def __del__(self):
        self.close()


    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.XREQ)
        self.socket.connect(self.host)


    def Get(self, key):
        self.socket.send_multipart(['GET', json.dumps([key])])
        return self.socket.recv_multipart()[0]


    def Put(self, key, value):
        self.socket.send_multipart(['PUT', json.dumps([key, value])])
        return self.socket.recv_multipart()[0]


    def Delete(self, key):
        self.socket.send_multipart(['DELETE', json.dumps([key])])
        return self.socket.recv_multipart()[0]


    def Range(self, start=None, end=None):
        self.socket.send_multipart(['RANGE', json.dumps([start, end])])
        return self.socket.recv_multipart()[0]


    def close(self):
        self.socket.close()
        self.context.term()
