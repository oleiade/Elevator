========
Elevator
========

.. image:: http://dl.dropbox.com/u/2497327/baneer.png
    :target: http://elevator.readthedocs.org

Elevator is an open source, on-disk key-value. It provides high-performance bulk read-write operations over very large datasets while exposing a simple and efficient API.

Written in Go, relying on the levelDB library as a storage backend, it provides a fast, async, and reliable access to a multi-db backend. Built upon the zeromq network library and msgpack serialization format it is made to be portable between languages and platforms.

Elevator is an open source software under the MIT license. Any hackers are welcome to supply ideas, features requests, patches, Pull requests and so on. Documentation’s development page contains comprehensive info on contributing, repository layout, our release strategy, and more.

See `Documentation <http://elevator.readthedocs.org>`_ for more details

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/Elevator&title=Elevator&language=&tags=github&category=software


Dependencies
============

::

  zmq-3.X
  leveldb >= 1.6


Debian repository
-----------------

The ``deb.oleiade.com`` debian repository exposes ``libzmq3``, ``libzmq3-dev``, ``libleveldb1`` and ``libleveldb1-dev`` packages in order to ease your dependencies management. Just add the following line to your ``/etc/apt/sources.list``:

.. code-block:: bash

  $ gpg --keyserver pgp.mit.edu --recv-keys A9171B8592EDE36B
  $ gpg --armor --export A9171B8592EDE36B | apt-key add -
  $ echo "deb http://deb.oleiade.com/debian oneiric main" >> /etc/apt/sources.list


Puppet
------

In order to ease your Elevator deployment, a `puppet module <http://github.com/oleiade/puppet-elevator>`_ has been developed. Note that it will automatically add the debian repository to your nodes.


Installation
============

Just make it
------------

1. First, make sure you have a `Go <http://http://golang.org/>`_ language compiler ``>= 1.1`` and `git <http://gitscm.org>`_ installed.

2. Then, clone this repository

.. code-block:: bash

  git clone git@github.com:oleiade/Elevator

3. Last, build and copy to a system ``PATH`` location

.. code-block:: bash

  cd Elevator
  make VERBOSE=1
  sudo cp ./bin/elevator /usr/local/bin/elevator


Docker
------

For the lazy guys out there, a Dockerfile is available at repositories top-level. It will allow you to build a `Docker <http://docker.io/>`_ container preconfigured for Elevator.

Once you've got `Docker <http://docker.io>`_ up and running on your system, just::

  docker build < Dockerfile
  docker run mysupperduppernewimagehash

You've got an up and running elevator container ready to serve. Enjoy!


Usage
=====

Once Elevator is installed, you can launch the server using the elevator executable.

.. code-block:: bash


  $ elevator -h

  Usage of ./bin/elevator:

  -e="127.0.0.1": If tcp transport is selected: ip the server
                  socket should be listening on.
  -c="/etc/elevator/elevator.conf": Path to elevator server
                                    config file, eventually
  -d=false: Launch elevator as a daemon
  -l="DEBUG": Log level, see python logging documentation
                            for more information :
                            http://docs.python.org/library/logging.html#logger-objects
  -p=4141: Port the server should listen on
  -t="tcp": Transport layer : tcp | ipc

You'll probably want to use the ``-d`` option, which will run Elevator in daemon mode. Elevator will then run in the background and will handle it's pid through the configuration defined ``pidfile``.

.. code-block:: bash

    $ elevator -d &



Configuration
=============

Server configuration relies on a INI file you can pass it as ``–c`` argument. As a default
Elevator will search for it's configuration at ``/etc/elevator/elevator.conf``

**example config (config/elevator.conf)**

.. code-block:: ini

  ### MANDATORY ###

  [core]
  # By default Elevator does not run as a daemon.
  # Use 'yes' if you need it. Note that Elevator will write
  # a pid file in /var/run/elevator.pid when daemonized.
  daemonize = false

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

  # Sets the logging verbosity, possible values are:
  # DEBUG, FINEST, FINE, DEBUG, TRACE,
  # INFO, WARNING, ERROR, CRITICAL
  log_level=INFO

  # Path to file were server activity should be logged
  log_file = /var/log/elevator.log


  ### OPTIONAL ###

  [storage_engine]

  # Whether data compaction using snappy should be activated
  # or not at the storage engine level.
  compression=true

  # Approximate size (in bytes) of user data packed per block. For very
  # large databases bigger block sizes are likely to perform better.
  # Default: 128K
  block_size=131072

  # The cache size (in bytes) determines how much data LevelDB caches in memory.
  # The more of your data set that can fit in-memory, the better LevelDB will perform.
  # Default: 512M
  cache_size=536870912

  # Larger write buffers increase performance, especially during bulk loads.
  # Up to two write buffers may be held in memory at the same time, so you may
  # wish to adjust this parameter to control memory usage.
  # Default: 64M
  write_buffer_size=67108864

  # Bloom filter will reduce the number of unnecessary disk reads needed for Get()
  # calls by a factor of approximately a 100.
  # Increasing the bits per key will lead to a larger reduction at the cost of more memory usage.
  bloom_filter_bits=100

  # Number of open files that can be used by the DB. You may need to increase this if your database has a large working set.
  max_open_files=150

  # If true, all data read from underlying storage will be verified against corresponding checksums.
  verify_checksums=false


Clients
=======

*Python*: `py-elevator <http://github.com/oleiade/py-elevator>`_

*Go*: `go-elevator <http://github.com/oleiade/go-elevator>`_ (Early early, so early version)

*Clojure* : *Coming soon*

*C* : *Coming soon*


Thanks
======

I wish to thank `Botify <http://botify.com>`_ which hires me and gave me the opportunity to spend some time on the project. To `Francisco Roque <http://www.franciscoroque.com/blog/>`_ and `BioQl <http://bioql.com/>`_ for their active support and feedback. Thanks to `Greg leclercq <https://twitter.com/ggregl>`_ for it's great advices and clever ideas.

I'd really like to thanks the `Zeromq <http://zeromq.org>`_ and `Leveldb <http://code.google.com/p/leveldb/>`_ creators and maintainers for their amazing work, without which, none of this would have been possible.

