.. _api:

============
Commands Api
============

.. _atomic_operations:

Atomic operations
=================

GET
---

Retrieves a value from a database

* params :
    * **key** : key to fetch

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "GET",
        "abc"
    ]

* typical response::

    [
        1,      # SUCCESS_STATUS
        -1,
        "",
        "123"
    ]


PUT
---

Inserts a value into a database

* params :
    * **key** : key to insert
    * **value** : value to insert

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "PUT",
        "abc",
        "123",
    ]

* typical response::

    [
        1,      # SUCCESS_STATUS
        -1,
        "",
        nil
    ]


DELETE
------

Deletes a key from a database

* params :
    * **key** : key to delete

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "DELETE",
        "abc"
    ]

* typical response::

    [
        1,      # SUCCESS_STATUS
        -1,
        "",
        nil
    ]


.. _bulk_operations:

Bulk operations
===============

MGET
----

Transactional bulk Get. Retrieves a list of keys values from a frozen database state.

* params :
    * **key1**, **key2**, ..., **keyn** : keys to fetch

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "MGET",
        "first",
        "second",
        "third"
    ]

* typical response::

    [
        1,      # SUCCESS_STATUS
        -1,
        "",
        "1",
        "2",
        "3"
    ]

RANGE
-----

Retrieves a range of key/value pairs from a database

* params :
    * **key_from** : key to start from
    * **key_to** : key where to stop

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "RANGE",
        "first",    # key from
        "third"     # key to
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        "first",    # key
        "1",        # value
        "second",   # key
        "2",        # value
        "third",    # key
        "3"         # value
    ]


SLICE
-----

Extracts a slice (key/value pairs) from a database

* params :
    * **key_from** : key to start from
    * **offset** : slice size

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "SLICE",
        "first",    # key from
        "3"         # offset
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        "first",    # key
        "1",        # value
        "second",   # key
        "2",        # value
        "third",    # key
        "3"         # value
    ]

BATCH
-----

Atomically applies all batch operations server-side

* params :
    * **operation1**, **operation-arg1**, **operation-arg2** ... : operations to execute server-side. Sequences of Batch operation signal and arguments.

* typical request::

    [
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
        "BATCH",
        "BPUT",         # Batch PUT operation signal
        "abc",          # Operation first arg
        "123",          # Operation second arg
        "BPUT",         # Batch PUT operation signal
        "easy as",      # Operation first arg
        "do re mi",     # Operation second arg
        "BDEL",         # Batch DEL operation signal
        "Jackson 5"     # Operation first arg
    ]

* typical response::

    [
        1,  (SUCCESS_STATUS),
        -1,
        "",
        nil
    ]


.. _databases_operations:

Databases operations
====================

DBCONNECT
---------

Retrieves a database uid from it's name. You can then use that uid to run commands over it.

* params :
    * **db_name** : database name to retrieve uid from

* typical request::

    [
        "",
        "DBCONNECT",
        "db name"
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        "3a4d1416-b6bd-4fbf-b415-0efa868ff27c",
    ]


DBMOUNT
-------

Tells Elevator to mount a database. As a default, Elevator only mounts the 'default' database. You can only run commands over mounted database. Mounted database fills the Elevator cache, and increases Ram memory consomation.

* params :
    * **db_name** : database name to mount

* typical request::

    [
        "",
        "DBMOUNT",
        "db name"
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        nil,
    ]


DBUMOUNT
--------

Tells Elevator to unmount a database, it is then unaccessible until you re-mount it. As a default, every databases except 'default' are unmounted. Once a database is unmounted Elevator tries to free as much cache it used as possible.

* params :
    * **db_name** : database name to unmount

* typical request::

    [
        "",
        "DBUMOUNT",
        "db name"
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        nil
    ]


DBCREATE
--------

Creates a new database

* params :
    * **db_name** : name of the created database
    * **db_options** : options to create database with

* typical request::

    [
        "",
        "DBCREATE",
        "db name"
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        nil,
    ]


DBLIST
------

Lists server's databases

* typical request::

    [
        "",
        "DBLIST",
        ""
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        "default",  # First db
        "testdb"    # Second db
    ]

DBREPAIR
--------

Repairs a broken (or too slow) database

**Notes** :
    * ``errors`` : In order not to expose too much information about Elevator internal errors to the client, only simple but explicit enough errors will be thrown by the database management commands. But, more (useful) informations will be logged in errors logs.

* typical request::

    [
        "",
        "DBREPAIR",
        "testdb"
    ]

* typical response::

    [
        1,          # SUCCESS_STATUS
        -1,
        "",
        nil
    ]
