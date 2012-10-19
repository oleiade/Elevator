========
Elevator
========

About
=====

Elevator is a Key-Value store written in Python and based on levelDB. It allows high performance on-disk bulk read/write. Provides async, multithreaded and/or remote access to a multi-leveldb backend.

Relies on the zeromq network library and msgpack serialization format as a messaging protocol. It was made to be portable between languages and platforms.


Installation
============

::

    $ pip install fabric
    $ fab build
    $ pip install -r requirements.txt
    $ python setup.py install

**Nota** : Elevator depends on `zmq <http://zeromq.org>`_ and `leveldb <http://code.google.com/p/leveldb/>`_ and both their respective python clients
`py-leveldb <http://code.google.com/p/py-leveldb>`_ and `pyzmq <https://github.com/zeromq/pyzmq>`_


Usage
=====

::

    $ elevator --help
    usage: elevator [-h]
                    [--daemon]
                    [--config CONFIG FILE]
                    [--bind BIND]
                    [--port PORT]
                    [--workers WORKERS COUNT]
                    [--paranoid SHOULD IT BREAK ON UNHANDLED EXCEPTIONS?]

    Elevator command line manager

    optional arguments:
        -h, --help    show this help message and exit
        --daemon      Launch elevator as a daemon
        --config      Path to elevator server config file, eventually
        --bind        Ip to bind server to
        --port        Port the server should listen on
        --workers     How many workers should be spawned (Threads
                      with concurrent access to all the db store)
        --paranoid    If option is set, Elevator will shutdown
                      and log on first unhandled exception

API
~~~

The **core** API is loosely defined as those functions, classes and methods
which form the basic building blocks of Fabric (such as
`~fabric.operations.run` and `~fabric.operations.sudo`) upon which everything
else (the below "contrib" section, and user fabfiles) builds.

.. toctree::
    :maxdepth: 1
    :glob:

    api/core/*

.. _contrib-api:


FAQ
---

Some frequently encountered questions, coupled with answers/solutions/excuses,
may be found on the :doc:`faq` page.

.. _api_docs:

Changelog
---------

Please see :doc:`the changelog </changelog>`.

Bugs/ticket tracker
-------------------

To file new bugs or search existing ones, you may visit Elevator's `Github Issues
<https://github.com/oleiade/Elevator/issues>`_ page. This does require a (free, easy to set up) Github account.
