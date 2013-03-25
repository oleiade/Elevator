========
Elevator
========

.. image:: http://dl.dropbox.com/u/2497327/baneer.png
    :target: http://elevator.readthedocs.org

Key-Value store written in Python and based on levelDB, allows high performance on-disk bulk read/write.

Allows async, multithreaded and/or remote access to a multi-leveldb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and
platforms.

See `Documentation <http://elevator.readthedocs.org>`_ for more details


Elevator is an open source software under the MIT license. Any hackers are welcome to supply ideas, features requests, patches, Pull requests and so on.  `Documentation's development page <http://elevator.readthedocs.org>`_ contains comprehensive info on contributing, repository layout, our release strategy, and more.

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/Elevator&title=Elevator&language=&tags=github&category=software


Dependencies
============

- zmq-3.X
- leveldb
- pyzmq (built with zmq-3.X)
- plyvel


Debian repository
-----------------

The ``deb.oleiade.com`` debian repository exposes ``libzmq3``, ``libzmq3-dev``, ``libleveldb1`` and ``libleveldb1-dev`` packages in order to ease your dependencies management. Just add the following line to your ``/etc/apt/sources.list``:

.. code-block:: bash

    deb http://deb.oleiade.com/debian oneiric main


Puppet
------

In order to ease your Elevator deployment, a `puppet module <http://github.com/oleiade/puppet-elevator>`_ has been developed. Note that it will automatically add the debian repository to your nodes.


Installation
============

Just::

    pip install Elevator


Usage
=====

When elevator is installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in ``.pid`` file in ``/tmp``.

See ``config/elevator.conf`` for an example of Elevator configuration.

*Example*:

.. code-block:: bash

    $ elevator --help

    usage: elevator [-hdctbpwv]

    Elevator command line manager

    optional arguments:
      -h, --help            Show this help message and exit
      -d, --daemon          Launch elevator as a daemon
      -c, --config          Elevator config file path
      -t, --transport       Transport layer: tcp or ipc
      -b, --bind            Address the server will be binded to
      -p, --port            Port the server should listen on
      -w, --workers         Workers to be spawned count
      -v, --log-level       Log level, see python logging documentation
                            for more information :
                            http://docs.python.org/library/logging.html#logger-objects


Clients
=======

*Python*: `py-elevator <http://github.com/oleiade/py-elevator>`_

*Go*: `go-elevator <http://github.com/oleiade/go-elevator>`_ (Early early, so early version)

*Clojure* : *Coming soon*

*C* : *Coming soon*


Thanks
======

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
