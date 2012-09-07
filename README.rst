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

Server
~~~~~~
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

Client
~~~~~~
In order to communicate with elevator, a Python client is avalaible. You can use it through the Elevator object,
brought by the client module.

Here is a demo:
::
    >>> from elevator.client import Elevator
    >>> E = Elevator()  # N.B : connected to 'default'
    >>> Ebis = Elevator('testdb')  # You can even construct your client with desired db to connect to
    >>> E.connect('testdbbis')  # Or even rebind client to a new database
    >>> E.Put('abc', 'cba')
    >>> E.Get('abc')
    'cba'
    >>> E.Get('earthwindandfire')
    KeyError: "Key does not exist"
    >>> E.Delete('abc')
    >>> for i in xrange(10):
    ...     E.Put(str(i), str(i))
    >>> E.Range('1', '9')
    [['1','1'],
     ['2','2'],
     ['3', '3'],
     ['4', '4'],
     ['5', '5'],
     ['6', '6'],
     ['7', '7'],
     ['8', '8'],
     ['9', '9'],
    ]
    >>> E.Range('1', 2)
    [['1', '1'],
     ['2', '2'],
    ]
    >>> it = E.Range('1', 2)
    >>> list(it)
    [['1', '1'],
     ['2', '2'],
    ]

Batch are implemented too. They're very handy and very fast when it comes to write a lot of datas to the database.
See `LevelDB documentation <http://leveldb.googlecode.com/svn/trunk/doc/index.html>`_ for more informations.
Use it through the WriteBatch client module class. It has three base methods modeled on LevelDB's
Put, Delete, Write.

Example:
::
    >>> from elevator.client import WriteBatch, Elevator
    >>> batch = WriteBatch()  # N.B : port, host, and timeout options are available here
    >>> batch.Put('a', 'a')
    >>> batch.Put('b', 'b')
    >>> batch.Put('c', 'c')
    >>> batch.Delete('c')
    >>> batch.Write()
    >>> E = Elevator()
    >>> E.Get('a')
    'a'
    >>> E.Get('b')
    'b'
    >>> E.Get('c')
    KeyError: "Key does not exist"

Thanks
------

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
