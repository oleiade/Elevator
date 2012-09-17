========
Elevator
========

Minimalistic database engine written in Python and based on levelDB.

Allows async, multithreaded and/or remote acces to a multidb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and
platforms.


Dependencies
------------

- zmq
- pyzmq
- leveldb
- py-leveldb

Installation
------------

::

    pip install fabric
    fab build
    python setup.py install


Usage
-----


When elevator is installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in .pid file in /tmp.

See config/elevator.conf for an example of Elevator configuration.

Example:
::
    elevator --help
    usage: elevator [-h] [--daemon] [--config CONFIG] [--bind BIND] [--port PORT]

    Elevator command line manager

    optional arguments:
      -h, --help       show this help message and exit
      --daemon
      --config      Path to elevator server config file, eventually
      --bind        Ip to bind server to
      --port        Port the server should listen on

Clients
-------

*Python* : [py-elevator](http://github.com/oleiade/py-elevator)
*Clojure* : *Coming soon*
*C* : *Coming soon*


Thanks
------

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
