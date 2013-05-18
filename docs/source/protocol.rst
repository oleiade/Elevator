.. _protocol:

=======================
Protocol Specifications
=======================

.. _communicate with elevator:

Communicate with Elevator
=========================

Depending on your Elevator configuration, once running it will either listen on a ``tcp://`` or ``ipc://`` socket handled by `zeromq network library <http://http://www.zeromq.org/>`_, waiting for requests to come in.

Elevator uses zeromq ``XREP`` and ``XREQ`` sockets, so that every commands passed through sockets are signed with a client id hash. X sockets queues messages as they come in order to prevent overload.

Finally, Elevator sockets are set to communicate using `multipart messages <http://www.zeromq.org/blog:zero-copy>`_ to be able to keep apart responses headers and content for example.

If you're trying to implement a client, or just curious about how it really works, you can take a look at both `source code <http://github.com/oleiade/Elevator>`_ and `python client <http://github.com/oleiade/py-elevator>`_


.. _messages:

Messages
=======

Every messages exchanged between Elevator and clients consist in a serialized `msgpack <http://msgpack.org>`_ ``Array``. For a matter of simplicity, performances, and static typed languages compatibility the ``array`` data-structure was prefered to a ``hash-map`` (as in the past versions).

.. _requests:

Request
-------

Request messages array format goes like this:

::

    [
        db uid,
        command,
        first argument,
        ...,
        nth argument,
    ]

* **uid**, *string*: is the uid of the database the command should be ran against 
* **cmd**, *string*:  is the command you'd like the server to run
* **args**, **string(s)**: are the command arguments. 


**Example** of key-value insertion::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "PUT",
        "abc",
        "123"
    ]

*Will put the ``abc`` -> ``123`` key value pair into pointed database*

**Example** of multiple keys retrieval::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "MGET",
        "a",
        "b",
        "c",
        "1"
    ]

*Will order Elevator to retrieve ``a, b, c, 1`` keys value from pointed database*

.. _response:

Response
--------

::

    [
        status,
        error code,
        error message,
        first result data,
        ...
        nth result data,
    ]

* **status**, *integer*: response status emitted by the server, defined by ``SUCCESS_STATUS``  and ``FAILURE_STATUS`` constants_.

* **error code**, *integer*: Thrown error code, defined by ``*_ERROR`` messages constants_. Error codes describes the type of the error which occured server side during a command execution. **Beware** this field will be filled with ``-1`` value if no error was thrown.

* **error message**, **string**: Thrown error message. Error messages describes the possible reasons of the command execution failure. **Beware** this field will be filled with empty ``string`` value if no error was thrown.

* **result data**, *string(s)* Resulting data of your operation, they always come as a flat succession of values.It's to the client to re-arrange them as he wants. If no data were to be returned, the 4th response value will be filled with ``nil`` value.

**Example** of a ``GET`` operation over a valid key response::

    [
        1,  (SUCCESS_STATUS constant)
        -1,
        "",
        '123',
    ]

*Asked key value is ``123``, the operation was successful as ``SUCCESS_STATUS`` constant indicates, and ``error code``, ``error message`` fields are respectively set to -1 (no errors)  and empty string values*

**Example** of a failing ``DBCREATE`` operation response::

    [
        -1, (FAILURE_STATUS constant)
        6,  (DATABASE_ERROR constant)
        "Database already exists",
        nil,
    ]

*``error code`` and ``error message`` indicates that the database couldn't be created as it already exists. Result data is left ``nil``*

**Example** of a succesful MGET operation response::

    [
        -2,  (WARNING_STATUS constant)
        -1,
        "",
        "a",
        "",
        "c",
    ]

*The response came in WARNING_STATUS, indicating that the command was only partially succesfull. Indeed, the second result data is an empty string. Indicating that the second key asked by the MGET operation could not be retrieved. Instead of failing, ``MGET`` operation normal behavior is to return empty strings in place of not found keys and WARNING_STATUS* 

.. _constants:

(coming soon)

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
    * ``include_key`` : whether should keys be include in return values or not, default is ``True``
    * ``include_value``: whether should values be included in return values or not, default is ``True``

``SLICE`` : Extracts a slice (key/value pairs) from a database

* params :
    * ``key_from`` : key to start from
    * ``offset`` : slice size
    * ``include_key`` : whether should keys be include in return values or not, default is ``True``
    * ``include_value``: whether should values be included in return values or not, default is ``True``

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
    * ``errors`` : In order not to expose too much information about Elevator internal errors to the client, only simple but explicit enough errors will be thrown by the database management commands. But, more (useful) informations will be logged in errors logs.

.. _database options:

Database Options
~~~~~~~~~~~~~~~~~~~~~

As Elevator uses `leveldb <http://http://code.google.com/p/leveldb/>`_ as a storage backend,
you can operate a rather precise configuration of your databases using leveldb backend.
Options covers database high level behavior, filesystem operations,
and cache management. You can find more details about configuration in `leveldb documentation
<http://leveldb.googlecode.com/svn/trunk/doc/index.html>`_

Here is a description offered by `py-leveldb <http://http://code.google.com/p/py-leveldb/>`_ of the available options.

.. code-block::ini

    create_if_missing  #(default: True)  if True, creates a new database if none exists
    error_if_exists    #(default: False)  if True, raises and error if the database already exists
    paranoid_checks    #(default: False)  if True, raises an error as soon as an internal corruption is detected
    block_cache_size   #(default: 8 * (2 << 20))  maximum allowed size for the block cache in bytes
    write_buffer_size  #(default  2 * (2 << 20))
    block_size         #(default: 4096)  unit of transfer for the block cache in bytes
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

        .. code-block::python
            [BATCH_OPERATION_SIGNAL, 'key', 'value if needed (Put)]

**Nota** : operations are treated server-side as signal. Batches exposes two signals:

.. code-block::python

    BATCH_SIGNAL_PUT = 1
    BATCH_SIGNAL_DELETE = 0

.. _pipelines:

Pipelines
============

(soon)

