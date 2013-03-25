:orphan:

Welcome to Elevator
===================

Welcome to Elevator's documentation. Elevator is a Key-Value store written
in Python and based on levelDB allowing high performance on-disk bulk read/write.
And provides async, multithreaded and/or remote access to a multi-leveldb backend.

It Relies on the zeromq network library and msgpack serialization format as a messaging protocol.
It was made with portability, stability, and focus on performance in mind.

Elevator depends on `zmq <http://zeromq.org>`_ and `leveldb <http://code.google.com/p/leveldb/>`_ and both their respective python clients `plyvel <https://github.com/wbolster/plyvel>`_ and `pyzmq <https://github.com/zeromq/pyzmq>`_

Elevator is an open source software under the MIT license. Any hackers are welcome to supply ideas, features requests, patches, Pull requests and so on.  `Documentation's development page <http://elevator.readthedocs.org>`_ contains comprehensive info on contributing, repository layout, our release strategy, and more.


.. include:: contents.rst.inc
