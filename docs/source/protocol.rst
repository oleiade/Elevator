.. _protocol:

=======================
Protocol Specifications
=======================

.. _communicating_with_elevator:

Communicating with Elevator
===========================

Depending on your Elevator configuration, once running it will either listen on a ``tcp://`` or ``ipc://`` socket handled by `zeromq network library <http://http://www.zeromq.org/>`_, waiting for requests to come in.

Elevator uses zeromq ``ROUTER`` and ``DEALER`` sockets, so that every commands passed through sockets are signed with a client id hash. X sockets queues messages as they come in order to prevent overload.

Finally, Elevator sockets are set to communicate using `multipart messages <http://www.zeromq.org/blog:zero-copy>`_ to be able to keep apart responses headers and content for example.

If you're trying to implement a client, or just curious about how it really works, you can take a look at both `source code <http://github.com/oleiade/Elevator>`_ and `python client <http://github.com/oleiade/py-elevator>`_


.. _messages_format:

Messages format
===============

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

Constants
=========

Responses status
----------------

::

    SUCCESS_STATUS = 1
    FAILURE_STATUS = -1
    WARNING_STATUS = -2


Responses error codes
---------------------

::

    TYPE_ERROR     = 0
    KEY_ERROR      = 1
    VALUE_ERROR    = 2
    INDEX_ERROR    = 3
    RUNTIME_ERROR  = 4
    OS_ERROR       = 5
    DATABASE_ERROR = 6
    SIGNAL_ERROR   = 7
    REQUEST_ERROR  = 8

Commands codes
--------------

::

    DB_GET     = "GET"
    DB_PUT     = "PUT"
    DB_DELETE  = "DELETE"
    DB_RANGE   = "RANGE"
    DB_SLICE   = "SLICE"
    DB_BATCH   = "BATCH"
    DB_MGET    = "MGET"
    DB_PING    = "PING"
    DB_CONNECT = "DBCONNECT"
    DB_MOUNT   = "DBMOUNT"
    DB_UMOUNT  = "DBUMOUNT"
    DB_CREATE  = "DBCREATE"
    DB_DROP    = "DBDROP"
    DB_LIST    = "DBLIST"
    DB_REPAIR  = "DBREPAIR"

Batch command sub-operations codes
----------------------------------

::

    SIGNAL_BATCH_PUT    = "BPUT"
    SIGNAL_BATCH_DELETE = "BDEL"




