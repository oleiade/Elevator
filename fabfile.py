#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import *


#
# DEPENDENCIES BUILD
#
def _build_pyleveldb():
    with lcd('/tmp'):
        local('svn checkout http://py-leveldb.googlecode.com/svn/trunk/ py-leveldb-read-only')
        with lcd('py-leveldb-read-only'):
            local('chmod -R 777 .')
            local('sh compile_leveldb.sh')
            local('python setup.py install')


def _build_zmq3x():
    with lcd('/tmp'):
        local('wget http://download.zeromq.org/zeromq-3.2.0-rc1.tar.gz;'
              'tar xf zeromq-3.2.0-rc1.tar.gz')
        with lcd('zeromq-3.2.0'):
            local('chmod -R 777 .')
            local('./autogen.sh ; ./configure')
            local('make ; sudo make install')


@task
def build():
    _build_pyleveldb()
    _build_zmq3x()

