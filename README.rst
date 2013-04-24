========
Elevator
========

.. image:: http://dl.dropbox.com/u/2497327/baneer.png
    :target: http://elevator.readthedocs.org

High performance on-disk Key-Value store.

Written in Go, relying on the leveldb library as a storage backend, `Elevator <http://github.com/oleiade/Elevator>`_ provides  a fast, async, and reliable access to a multi-leveldb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and platforms.

See `Documentation <http://elevator.readthedocs.org>`_ for more details


Elevator is an open source software under the MIT license. Any hackers are welcome to supply ideas, features requests, patches, Pull requests and so on.  `Documentation's development page <http://elevator.readthedocs.org>`_ contains comprehensive info on contributing, repository layout, our release strategy, and more.

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/Elevator&title=Elevator&language=&tags=github&category=software


Dependencies
============

- zmq-3.X
- leveldb >= 1.6

As of today, the Elevator provided Makefile will download, build, and compile on-time against ``leveldb``, 
so you don't need to bother about it. But, though it might not be necessary in the future, installing ``libzmq3`` and ``libzmq3-dev`` system wide is mandatory.


Debian repository
-----------------

The ``deb.oleiade.com`` debian repository exposes ``libzmq3``, ``libzmq3-dev`` packages in order to ease your dependencies management. Just add the following line to your ``/etc/apt/sources.list``:

.. code-block:: bash

    deb http://deb.oleiade.com/debian oneiric main


Puppet
------

In order to ease your Elevator deployment, a `puppet module <http://github.com/oleiade/puppet-elevator>`_ has been developed. Note that it will automatically add the debian repository to your nodes.


Installation
============

1. First, make sure you have a `Go <http://http://golang.org/>`_ language compiler and `git <http://gitscm.org>`_ installed.

2. Then, clone this repository::
  
  git clone git@github.com:oleiade/Elevator

3. Last, build and copy to a system ``PATH`` location

  cd Elevator
  make VERBOSE=1
  sudo cp ./bin/elevator /usr/local/bin/elevator


Usage
=====

Once Elevator is installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in ``.pid`` file in ``/tmp``.

See ``config/elevator.conf`` for an example of Elevator configuration.

*Example*:

.. code-block:: bash


  $ elevator -h

  Usage of ./bin/elevator:
  
  -b="127.0.0.1": If tcp transport is selected: ip the server
                  socket should be listening on.
  -c="/etc/elevator/elevator.conf": Path to elevator server 
                                    config file, eventually
  -d=false: Launch elevator as a daemon
  -l="DEBUG": Log level, see python logging documentation
                            for more information :
                            http://docs.python.org/library/logging.html#logger-objects
  -p=4141: Port the server should listen on
  -t="tcp": Transport layer : tcp | ipc


Configuration
=============

Server configuration relies on a INI file you can pass it as ``–c`` argument. As a default
Elevator will search for it's configuration at ``/etc/elevator/elevator.conf``

**example config (config/elevator.conf)**

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

  # Endpoint the server should be binded on. Disposable transport
  # layer are tcp and ipc. So for example if you wanna set elevator
  # to listen on a unixsocket, you might set this value to 
  # ipc:///tmp/elevator.sock
  endpoint = tcp://127.0.0.1:4141

  # Path to file were server activity should be logged
  activity_log = /var/log/elevator.log

  # Path to file were server warnings, errors, exceptions should be logged
  errors_log = /var/log/elevator_errors.log


Clients
=======

*Python*: `py-elevator <http://github.com/oleiade/py-elevator>`_

*Go*: `go-elevator <http://github.com/oleiade/go-elevator>`_ (Early early, so early version)

*Clojure* : *Coming soon*

*C* : *Coming soon*

