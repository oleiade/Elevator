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
            local('sudo chmod -R 777 .')
            local('sudo sh compile_leveldb.sh')
            local('sudo python setup.py install')


def install_requirements():
    _build_pyleveldb()
    local('pip install -r requirements.txt')


def build():
    install_requirements()
