========
Elevator
========

Minimalistic database engine based on levelDB.
Allows async, multithreaded and/or remote acces to a leveldb backend.
Will implement soon more complex data structures such as List, Hashes, and Sets
as native parts of the Engine.
Relying on the zeromq network library, it is made to be portable between languages and
platforms.

N.B. Still very early release, should not be stable, and be warned that
many changes breaking backward compatibility are still possible.


In the development tasks stack
------------------------------

- Implement batching.
- Formalize a json api to communicate with server frontend and backend.
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

(Soon)

Thanks
------

Thanks to `srinikom <https://github.com/srinikom>`_ for its `leveldb-server <https://github.com/srinikom/leveldb-server>`_ which was a very good base to start from.
Thanks to Google, for its amazing database.
Thanks to ZeroMQ team, you changed my life!
