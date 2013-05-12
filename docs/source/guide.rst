.. _guide:

=============
Kickstarting
=============

.. _downloads:

Downloads
==========

The official downloads are located on `Elevator's Github repository Tags page <http://github.com/oleiade/Elevator/tags>`_.

Get the source code
====================

The Elevator developers manage the project’s source code with the Git. To get the latest major version source code, clone the canonical repository straight from the Elevator repository on Github:

.. code-block:: bash

    $ git://github.com/oleiade/Elevator.git

.. _dependencies:

Dependencies
==================

Elevator depends on:

* `Go >= 1.0 <http://golang.org>`_ language compiler
* `zmq <http://zeromq.org>`_ (>= 3.x)
* `leveldb <http://code.google.com/p/leveldb/>`_ (>= 1.6)


Debian repository
-----------------

The ``deb.oleiade.com`` debian repository exposes ``libzmq3``, ``libzmq3-dev``, ``libleveldb1`` and ``libleveldb1-dev`` packages in order to ease your dependencies management. Just add the following line to your ``/etc/apt/sources.list``:

.. code-block:: bash

  $ gpg --keyserver pgp.mit.edu --recv-keys A9171B8592EDE36B
  $ gpg --armor --export A9171B8592EDE36B | apt-key add -
  $ echo "deb http://deb.oleiade.com/debian oneiric main" >> /etc/apt/sources.list

  # Then you're ready to install leveldb and zmq 3.x libs
  $ sudo apt-get install libleveldb1 libleveldb-dev libzmq3 libzmq3-dev


Puppet
------

In order to ease your Elevator deployment, a `puppet module <http://github.com/oleiade/puppet-elevator>`_ has been developed. Note that it will automatically add the debian repository to your nodes.


.. _installation:

Installation
==================

1. First, make sure you have a `Go <http://http://golang.org/>`_ language compiler and `git <http://gitscm.org>`_ installed.

2. Then, clone this repository
  
.. code-block:: bash
  
  git clone git@github.com:oleiade/Elevator

3. Last, build and copy to a system ``PATH`` location

.. code-block:: bash

  cd Elevator
  make VERBOSE=1
  sudo cp ./bin/elevator /usr/local/bin/elevator

.. _usage:

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
      -c="/etc/elevator/elevator.conf": Specifies config file path
      -d=false: Launches elevator as a daemon
      -e="": Endpoint to bind elevator to
      -l="INFO": Sets elevator verbosity


.. _configuration:

Configuration
================

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
  databases_store_path = /var/lib/elevator

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
  # DEBUG, TRACE, INFO, WARNING, ERROR, CRITICAL
  log_level=INFO

  # Path to file were server activity should be logged
  activity_log = /var/log/elevator.log

  # Path to file were server warnings, errors, exceptions should be logged
  errors_log = /var/log/elevator_errors.log

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

