#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import *


#
# DEPENDENCIES BUILD
#
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
    _build_zmq3x()

