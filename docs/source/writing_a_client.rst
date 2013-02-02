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

**Nota**: Before you ask, yes, it is **mandatory** to use zeromq, to communicate with Elevator, as it relies on the `Router-Dealer <http://www.zeromq.org/sandbox:dealer>`_  pattern. 

Msgpack
-------

`msgpack <http://msgpack.org>`_ is a very lightweight serialization format, which is mostly compatible with json syntax. It will be used to serialize requests and responses. 


Establishing a connexion
========================

Global process
--------------

Establishing a connexion to an Elevator server goes like this:

1. Client uses a :ref:`Dealer socket <dealer-socket>` to send a :ref:`connexion request <connexion-protocol>` to the server
2. Client awaits for the server reponse
3. Server responds with the requested database connexion uid
4. Client can now use this database uid in all it's requests against it  

.. _dealer-socket:
Dealer socket
-------------

As told upper, Elevator server exposes a zeromq `Router <http://www.zeromq.org/sandbox:dealer>`_ socket which awaits for `Dealer <http://www.zeromq.org/sandbox:dealer>`_ sockets to connect to it. 

**Nota**: The specificity of Router-Dealer zeromq sockets is their queuing feature. Bascially, in order to enhance asycnhronous behaviors and load balancing a ROUTER socket queues incoming connexions and requests until it's able to forward it.

.. _connexion-protocol:
Connexion Protocol
------------------

(coming soon)

Request messages
----------------

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
