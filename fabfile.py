#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import *


#
# DEPENDENCIES BUILD
#
def _build_zeromq():
    with lcd('/tmp'):
        local('wget http://download.zeromq.org/zeromq-2.2.0.tar.gz')
        local('tar xvfz zeromq-2.2.0.tar.gz')
        with lcd('zeromq-2.2.0'):
            local('sudo ./configure')
            local('sudo chmod -R 777 .')
            local('make')


def _build_pyzmq():
    with lcd('/tmp'):
        local('wget http://pypi.python.org/packages/source/p/pyzmq/pyzmq-2.1.11.tar.gz')
        local('tar xvfz pyzmq-2.1.11.tar.gz')
        with lcd('pyzmq-2.1.11'):
            local('sudo python setup.py configure --zmq=/usr/local')
            local('sudo chmod -R 777 .')
            local('sudo python setup.py install')


def _build_pyleveldb():
    with lcd('/tmp'):
        local('svn checkout http://py-leveldb.googlecode.com/svn/trunk/ py-leveldb-read-only')
        with lcd('py-leveldb-read-only'):
            local('sudo chmod -R 777 .')
            local('sudo sh compile_leveldb.sh')
            local('sudo python setup.py install')


def _build_thrift():
    with lcd('/tmp'):
        local('wget http://mirror.speednetwork.de/apache/thrift/0.8.0/thrift-0.8.0.tar.gz')
        local('tar xvfz thrift-0.8.0.tar.gz')
        with lcd('thrift-0.8.0'):
            local('sudo chmod -R 777 .')
            local('./configure')
            local('make')
            local('sudo make install')


def install_dependencies():
    _build_zeromq()
    _build_thrift()


def install_requirements():
    _build_pyzmq()
    _build_pyleveldb()
    local('pip install -r requirements.txt')


def build():
    install_dependencies()
    install_requirements()
