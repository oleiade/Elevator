:orphan:

Welcome to Elevator
===================

Welcome to Elevator's documentation.

Elevator is a high performance on-disk Key-Value store.

Written in Go, relying on the levelDB library as a storage backend, it provides a fast, async, and reliable access to a multi-db backend.

It exposes a simple and efficient API allowing the user to work around with fast large dataset through ``batches`` (Write operations) and ``ranges/slices`` (Read operations) and with classic atomic operations such as `GET` `PUT` and `DELETE`.

Built upon the zeromq network library and msgpack serialization format it is made to be portable between languages and platforms.


Elevator is an open source software under the MIT license. Any hackers are welcome to supply ideas, features requests, patches, Pull requests and so on.  `Documentation's development page <http://elevator.readthedocs.org>`_ contains comprehensive info on contributing, repository layout, our release strategy, and more.


.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: https://flattr.com/submit/auto?user_id=oleiade&url=http://github.com/oleiade/Elevator&title=Elevator&language=&tags=github&category=software


.. include:: contents.rst.inc
