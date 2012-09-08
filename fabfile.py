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


@task
def install_requirements():
    _build_pyleveldb()
    local('pip install -r requirements.txt --use-mirrors')


@task
def build():
    install_requirements()
