.. _protocol:

===========
Protocol
===========

.. _communicate with elevator:

Communicate with elevator
==========================

Depending on your Elevator configuration, once running it will either listen on a ``tcp://`` or ``ipc://`` socket handled by zeromq network library, waiting for requests to come in.

Elevator uses zeromq ``XREP`` and ``XREQ`` sockets, so that every commands passed through sockets are signed with a client id hash. X sockets queues messages as they come in order to prevent overload.

Finally, Elevator sockets are set to communicate using `multipart messages <http://www.zeromq.org/blog:zero-copy>`_ to be able to keep apart responses headers and content for example.

If you're trying to implement a client, or just curious about how it really works, you can take a look at both `source code <http://github.com/oleiade/Elevator>`_ and `python client <http://github.com/oleiade/py-elevator>`_


.. _messages:

Messages
==========

Every messages exchanged between Elevator and clients consist in hash maps serialized using msgpack.
Hash maps is a common data structure present in most languages, it was used because of it's
simplicity, and similarity with json format, which many developpers are confortable with nowadays.
`Msgpack <http://msgpack.org>`_ is a very popuplar and performant serialization protocol ported to many languages.

.. _requests:

Request
-----------

Request messages format goes like this:

.. code-block:: json

    {
        "meta": { ... },
        "uid": string,
        "cmd": int,
        "args": [ string... ]
    }

* ``uid`` is the database affected by command uid
* ``cmd`` is the command you'd like the server to run
* ``args`` are the command arguments, nota that they should be in the order commands defines.
* ``meta`` are the options you'd wish the server to take in account when dealing with your request.


*example*::

    {
        "meta": {
            "compression": true,
        }
        "uid": "theamazingdatabasewewannaupdatemd5hash",
        "cmd": "PUT",
        "args": ["key", "value"],
    }


.. _response:

Response
------------

Responses comes into two parts (multipart). First response part is the Header,
and the second one is the content.

.. _header:

Header
~~~~~~~~~~~

.. code-block:: json

    {
        "meta": { ... },
        "status" : int,
        "err_code": int,
        "err_msg": string
    }

* ``status`` is the response status emitted by the server.

* ``err_code`` and ``err_msg`` if server encountered an error dealing with the request,
then an error code and error message will be present in response header.

* ``meta``  are the options the server to took in account when dealing with your request.
example : if compression was requested, the response header will come back with compression
meta too.


*example*::

    {
        "meta": {
            "compression": true,
        }
        "status": -1,
        "err_code": 0,
        "err_msg": "Key doesn't exist",
    }

.. _content:

Content
~~~~~~~~~~~~

Second response part is the content,
and the second one is the content.

.. code-block:: json

    {
        "datas": [ string... ],
    }


.. _meta:

Meta
~~~~~~~~~~~

As you might have noticed, both requests and response header have a meta field. Though it's presence is mandatory in requests
you can perfectly leave it as an empty hash map if you don't need it.

It's goal is to let the client and server set options when they're exchanging requests and response. Today, only one option is
supported, but their might be more coming as the development stream flows.

*Meta options*:

* ``compression`` : ``true`` | ``false``
    When you're dealing with huge masses of datas (and I mean, **really** huge), you might notice Elevator slowing
    down sometimes

    That's because of the Response size which has to be sent over network (when your dealing with Elevator on your local
    machine : generally ther's no problem). To fight the transfer time, and reduce the response size, Elevator can compress the responses
    using lz4.


.. _commands:

Commands
============

.. _basics:

Basics
--------

Server responds to some constants whenever it comes to give it commands. In the following listing, dbuid represents the database unique uid to operate the command over, it can be retrieved from a database name via 'CONNECT'. And batch_uid represents a valid server-side created batch (using BCREATE) to run commands over.

``GET`` : Retrieves a value from a database
    * params :
        * ``key`` : key to fetch

``MGET`` : Transactional bulk Get. Retrieves a list of keys values
on a frozen database state.
    * params :
        * [ ``key1``, ``key2``, ..., ``keyn + 1``] : keys to fetch value from

``PUT`` :  Inserts a value into a database
    * params :
        * ``key`` : key to insert
        * ``value`` : value to insert

``DELETE`` : Deletes a key from a database
    * params :
        * ``key`` : key to delete

``RANGE`` : Retrieves a range of key/value pairs from a database
    * params :
        * ``key_from`` : key to start from
        * ``key_to`` : key where to stop

``SLICE`` : Extracts a slice (key/value pairs) from a database
    * params :
        * ``key_from`` : key to start from
        * ``offset`` : slice size

.. _databases management:

Databases management
------------------------------

``DBCONNECT`` : Retrieves a database uid from it's name. You can
then use that uid to run commands over it.
    * params :
        * ``db_name`` : database name to retrieve uid from

``DBMOUNT`` : Tells Elevator to mount a database. As a default, Elevator
only mounts the 'default' database. You can only run commands over
mounted database. Mounted database fills the Elevator cache, and increases
Ram memory consomation.
    * params :
        * ``db_name`` : database name to mount

``DBUMOUNT`` : Tells Elevator to unmount a database, it is then
unaccessible until you re-mount it. As a default, every databases except
'default' are unmounted. Once a database is unmounted
Elevator tries to free as much cache it used as possible.
    * params :
        * ``db_name`` : database name to unmount

``DBCREATE`` : Creates a  new database
    * params :
        * ``db_name`` : name of the created database
        * ``db_options`` : options to create database with

``DBLIST`` : Lists server's databases

``DBREPAIR`` : Repairs a broken (or too slow) database you already owns uid

**Notes** :
    * ``errors`` : In order not to expose too much information about Elevator internal errors to the client,
    only simple but explicit enough errors will be thrown by the database management commands. But, more
    (useful) informations will be logged in errors logs.

.. _database options:

Database Options
~~~~~~~~~~~~~~~~~~~~~

As Elevator uses `leveldb <http://http://code.google.com/p/leveldb/>`_ as a storage backend,
you can operate a rather precise configuration of your databases using leveldb backend.
Options covers database high level behavior, filesystem operations,
and cache management. You can find more details about configuration in `leveldb documentation
<http://leveldb.googlecode.com/svn/trunk/doc/index.html>`_

Here is a description offered by `py-leveldb <http://http://code.google.com/p/py-leveldb/>`_ of the available options.

.. code-block:: ini

    create_if_missing  #(default: True)  if True, creates a new database if none exists
    error_if_exists      #(default: False)  if True, raises and error if the database already exists
    paranoid_checks   #(default: False)  if True, raises an error as soon as an internal corruption is detected
    block_cache_size  #(default: 8 * (2 << 20))  maximum allowed size for the block cache in bytes
    write_buffer_size  #(default  2 * (2 << 20))
    block_size            #(default: 4096)  unit of transfer for the block cache in bytes
    max_open_files:    #(default: 1000)



Options should be passed as a hash map with the ``DBCREATE`` function. It comes with default
values which will be overrided with the ones you set.


.. _batches:

Batches
---------

``BATCH`` : Atomically applies all batch operations server-side
    * params :
        * [ ``operation1``, ``operation2``, ..., ``operation_n + 1``] : operations to
        execute server-side. Pairs of Batch operation signal and arguments.
        example:

        .. code-block:: python

            [BATCH_OPERATION_SIGNAL, 'key', 'value if needed (Put)]

**Nota** : operations are treated server-side as signal. Batches exposes two signals:

.. code-block:: python

    BATCH_SIGNAL_PUT = 1
    BATCH_SIGNAL_DELETE = 0

.. _pipelines:

Pipelines
============

(soon)

