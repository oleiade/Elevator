========
Elevator
========

.. image:: http://dl.dropbox.com/u/2497327/baneer.png
    :target: http://elevator.readthedocs.org

Key-Value store written in Python and based on levelDB, allows high performance on-disk bulk read/write.

Allows async, multithreaded and/or remote access to a multi-leveldb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and
platforms.

See `Documentation <http://oleiade.github.com/Elevator>`_ for more details

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/Elevator&title=Elevator&language=&tags=github&category=software


Depends on
----------

- zmq-3.X
- pyzmq (built with zmq-3.X)
- leveldb
- plyvel


Installation
============

The easy way::

    pip install elevator

The hacker way::

    $ pip install fabric
    $ fab build
    $ pip install -r requirements.txt
    $ python setup.py install


Usage
=====

When elevator is installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in ``.pid`` file in ``/tmp``.

See ``config/elevator.conf`` for an example of Elevator configuration.

*Example*:

.. code-block:: bash

    $ elevator --help
    usage: elevator -h

    Elevator command line manager

    optional arguments:
        -h, --help       show this help message and exit
        -d, --daemon      Launch elevator as a daemon
        -c, --config      Path to elevator server config file, eventually
        -t, --transport   Transfert protocol (tcp | ipc)
        -b, --bind        Ip to bind server to
        -p, --port        Port the server should listen on
        -w, --workers     How many workers should be spawned (Threads with concurrent access to all the db store)
        -P, --paranoid    If option is set, Elevator will shutdown and log on first unhandled exception


Clients
=======

*Python*: `py-elevator <http://github.com/oleiade/py-elevator>`_

*Go*: `go-elevator <http://github.com/oleiade/go-elevator>`_ (Early early, so early version)

*Clojure* : *Coming soon*

*C* : *Coming soon*


Thanks
======

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
