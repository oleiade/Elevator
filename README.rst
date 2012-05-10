========
Elevator
========

Minimalistic database engine written in Python an based on levelDB.
Allows async, multithreaded and/or remote acces to a leveldb backend.
Will implement soon more complex data structures such as List, Hashes, and Sets
as native parts of the Engine.
Relying on the zeromq network library, it is made to be portable between languages and
platforms.

N.B. Still very early release, should not be stable, and be warned that
many changes breaking backward compatibility are still possible.


In the development tasks stack
------------------------------
- Formalize a rpc interface using protocol buffers between client and server.
- Being able to handle complex data structures using protocol buffer.

Dependencies
------------

- pyzmq
- leveldb
- snappy
- py-leveldb

Installation
------------

::

    pip install fabric
    fab install_dependencies
    python setup.py install

Usage
-----

Server
~~~~~~
When elevator installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in .pid file in /tmp.

Example:
::
    elevator --help
    usage: elevator [-h] [--daemon] [--config CONFIG] [--bind BIND] [--port PORT]
                    [--db DB]

    Elevator command line manager

    optional arguments:
      -h, --help       show this help message and exit
      --daemon
      --config CONFIG
      --bind BIND
      --port PORT
      --db DB

Client
~~~~~~
In order to communicate with elevator, a python client is avalaible. You can use it through the Elevator object,
brought by the elevator.client module.

Here is a demo:
::
    >>> from elevator.client import Elevator
    >>> E = Elevator()  # N.B : port, host, and timeout options are available here
    >>> E.Put('abc', 'cba')
    'True'
    >>> E.Get('abc')
    'cba'
    >>> E.Delete('abc')
    ''
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

Batch are implemented too. They're very handy and very fast when it comes to write a lot of datas to the database.
See `LevelDB documentation <http://leveldb.googlecode.com/svn/trunk/doc/index.html>` for more informations.
Use it through the WriteBatch client module class. It has three base methods modeled on LevelDB's
Put, Delete, Write.

Example:
::
    >>> from elevator.client import WriteBatch, Elevator
    >>> batch = WriteBatch()  # N.B : port, host, and timeout options are available here
    >>> batch.Put('a', 'a')
    ''
    >>> batch.Put('b', 'b')
    ''
    >>> batch.Put('c', 'c')
    ''
    >>> batch.Delete('c')
    ''
    >>> batch.Write()
    ''
    >>> E = Elevator()
    >>> E.Get('a')
    'a'
    >>> E.Get('b')
    'b'
    >>> E.Get('c')
    ''  # Errors will be implemented soon!

Thanks
------

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
Thanks to Google, for its amazing database.
Thanks to ZeroMQ team, you changed my life!
