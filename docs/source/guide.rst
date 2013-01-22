.. _guide:

=============
Kickstarting
=============

.. _downloads:

Downloads
==========

The official downloads are located on `Elevator's Github repository Tags page <http://github.com/oleiade/Elevator/tags>`_. I will be soon available on Pypi...

Get the source code
====================

The Elevator developers manage the project’s source code with the Git. To get the latest major version source code, clone the canonical repository straight from the Elevator repository on Github:

.. code-block:: bash

    $ git://github.com/oleiade/Elevator.git

.. _dependencies:

Dependencies
==================

Elevator depends on:

* `Python <www.python.org>`_ language
* the `setuptools` packaging/installation library
* `zmq <http://zeromq.org>`_ (>= 2.2, zmq3.x is supported too)
* `leveldb <http://code.google.com/p/leveldb/>`_ (>= 1.6)

    * `libleveldb1` and `libleveldb-dev` should be disposable on most **linux** distributions, if it's not yet ported to yours, just checkout the leveldb source code, `make` and cp the libray files ('.so') to /usr/local/lib, and don't forget to add /usr/local/lib to your libpath.

    * `leveldb` is disposable on *Homebrew* for **Osx** and I guess it might be too on *ports*

* Python packages listed in `requirements.txt`

Python
-----------

Elevator requires Python version 2.6 or 2.7. It has not yet been tested on Python 3.x and is thus likely to be incompatible with it.

Setuptools
-----------------

Setuptools comes with some Python installations by default; if yours doesn’t, you’ll need to grab it. In such situations it’s typically packaged as python-setuptools, py27-setuptools or similar.


Zmq and Leveldb
--------------------

Elevator requires `zmq <http://zeromq.org>`_ and `leveldb <http://code.google.com/p/leveldb/>`_ libraries are installed on the system. Most unix systems provides
these libraries through their package managers. For example, debian provides both a libleveldb1 and libleveldb-dev packages and libzmq-dev. On osx, you would be able to install them using brew.

Anyway, Elevator is shipped with a fabfile included and rules to automatically download, compile, and install
both leveldb and zmq libraries. To use it, you'll need `fabric <http://docs.fabfile.org/>`_ installed.

Just run:

.. code-block:: bash

    $ fab build.all


.. _installation:

Installation
==================

We consider here that you've succesfully installed leveldb >= 1.6 and libzmq in order
for python packages to build against compatible versions of the libs.

.. code-block:: bash

    $ python setup.py install

.. _usage:

Usage
=====

.. code-block:: bash

    $ elevator --help
    usage: elevator [-h] [-dctbpwPv]

    Elevator command line manager

    optional arguments:
        -h, --help        show this help message and exit

        -d, --daemon      Launch elevator as a daemon

        -c, --config      Path to elevator server config file, eventually

        -t, --transport   Transport layer : tcp | ipc

        -b, --bind        If tcp transport is selected: ip the server
                          socket should be listening on.

        -p, --port        Port the server should listen on

        -w, --workers     How many workers should be spawned (Threads
                          with concurrent access to all the db store)

        -P, --paranoid    If option is set, Elevator will shutdown
                          and log on first unhandled exception

        -v, --log-level   Log level, see python logging documentation
                          for more information :
                          http://docs.python.org/library/logging.html#logger-objects


.. _configuration:

Configuration
================

Server configuration relies on a INI file you can pass it as --config argument. All the configuration options key/value are then loaded in a server specific singleton Environment object, which any part of the server can eventually access.

**example config** (*config/elevator.conf*)


.. code-block:: ini

    [global]
    # By default Elevator does not run as a daemon.
    # Use 'yes' if you need it. Note that Elevator will write
    # a pid file in /var/run/elevator.pid when daemonized.
    daemonize = no

    # When running daemonized, Elevator writes
    # a pid file in /var/run/elevator.pid by default.
    # You can specify a custom pid file location here.
    pidfile = /var/run/elevator.pid

    # Where databases files should be store on the filesystem.
    databases_storage_path = /var/lib/elevator

    # Where should the file describing the databases store be
    # put on file system
    database_store = /var/lib/elevator/store.json

    #Default database
    default_db = default

    # Accept connections on the specified port, default is 4141.
    # If port 0 is specified Elevator will not listen on a TCP socket.
    port = 4141

    # If you want you can bind a single interface,
    # if the bind option is not specified all the interfaces
    #  will listen for incoming connections.
    bind = 127.0.0.1

    # Path to file were server activity should be logged
    activity_log = /var/log/elevator.log

    # Path to file were server warnings, errors, exceptions should be logged
    errors_log = /var/log/elevator_errors.log

    # Max global leveldb backends cache size in Mo.
    # Note that each spawned leveldb backend by default
    # has a max_cache_size. This LRU cache is used to preload
    # in memory key that you have already fetch
    # and accelerate random GET. In order not to overflow
    # the memory, max_cache_size ensures every backends
    # cache size cumulated does not exceed the provided value.
    max_cache_size = 1024

    # Specify the path for the unix socket that will be used to listen for
    # incoming connections when Elevator is set to use an ipc socket.
    # unixsocket = /tmp/elevator.sock


.. _clients:

Clients
=======

Command line (Experimental)
--------------------------------

Elevator is shipped with a built-in command line interface, so you can jump in without
setting up an external client.

Ensure that you've got an elevator server running, and you're done:

.. code-block:: bash

    $ elevator-cli

You'll probably want to consult the :ref:`Command line usage <cmdline>` section in order to learn more about
it's usage.

Languages clients
-----------------------

A few languages clients for Elevator exists already:

* `py-elevator <http://github.com/oleiade/py-elevator>`_ : Python client, stable
* `go-elevator <http://github.com/oleiade/go-elevator>`_ : Go client module, under heavy development
* `clj-elevator <http://github.com/oleiade/clj-elevator>`_ : Clojure client, under heavy development

Feel free to add your own and to ask for adding it here. See :ref:`protocol` for more details on how
to implement your own client in your language.


.. _deployment:

Deployment
============

(coming soon)
