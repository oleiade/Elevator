#!/usr/bin/env python
# -*- coding: utf-8 -*-


from fabric.api import *
from fabric.context_managers import quiet


#
# DEPENDENCIES BUILD
#
@task
def leveldb():
    """Locally builds and install leveldb system-wide"""
    with lcd('/tmp'):
        with quiet():
            local('mkdir leveldb_install')

        with lcd('leveldb_install'):
            local('svn checkout http://snappy.googlecode.com/svn/trunk/ snappy-read-only')

            with lcd('snappy-read-only'):
                local('./autogen.sh && ./configure --enable-shared=no --enable-static=yes')
                local("make clean && make CXXFLAGS='-g -O2 -fPIC'")

            local('git clone https://code.google.com/p/leveldb/ || (cd leveldb; git pull)')

            with lcd('leveldb'):
                local('make clean')
                local("make LDFLAGS='-L../snappy-read-only/.libs/ -Bstatic -lsnappy -shared' "
                            "OPT='-fPIC -O2 -DNDEBUG -DSNAPPY -I../snappy-read-only' "
                            "SNAPPY_CFLAGS='' ")

    sudo('cp -rf /tmp/leveldb_install/leveldb/libleveldb.so* /usr/local/lib')
    sudo('cp -rf /tmp/leveldb_install/leveldb/include/leveldb /usr/local/include')
    local('rm -rf /tmp/leveldb_install')


@task
def zmq():
    """Locally builds and install zeromq-3.2 system wide"""
    with lcd('/tmp'):
        local('wget http://download.zeromq.org/zeromq-3.2.0-rc1.tar.gz;'
              'tar xf zeromq-3.2.0-rc1.tar.gz')
        with lcd('zeromq-3.2.0'):
            local('chmod -R 777 .')
            local('./autogen.sh ; ./configure')
            local('make ; sudo make install')

    local('rm -rf /tmp/zeromq-3.2.0-rc1.tar.gz')


@task
def all():
    build_zmq()
    build_leveldb()
