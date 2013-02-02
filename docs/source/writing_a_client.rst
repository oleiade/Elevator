.. _writing_a_client:

================
Writing a client
================

Requirements
============

Communicating with Elevator relies on two mandatory dependencies, which fortunatly have been ported in many languages yet: 

* `zeromq <http://zeromq.org>`_ (>= 2.2, zmq3.x is supported too)
* `msgpack <http://msgpack.org/>`_.

Zeromq
------

`zeromq <http://zeromq.org>`_ is an overlay on top of sockets, it implements many commons communication patterns, and takes all the sockets handling pain away. It will be used to transport requests messages and receives responses to and from Elevator.

**Nota**: Before you ask, yes, it is **mandatory** to use zeromq, to communicate with Elevator, as it relies on the ROUTER/DEALER pattern. 

Msgpack
-------

`msgpack <http://msgpack.org>`_ is a very lightweight serialization format, which is mostly compatible with json syntax. It will be used to serialize requests and responses. 


Establishing a connexion
========================

(coming soon)


Sending commands
================

(coming soon)

Handling result
===============

(coming soon)

Remarks
=======

(coming soon)
