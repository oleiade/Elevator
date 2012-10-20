.. _usage:

Usage
=====

::

    $ elevator --help
    usage: elevator [-h]
                    [--daemon]
                    [--config CONFIG FILE]
                    [--bind BIND]
                    [--port PORT]
                    [--workers WORKERS COUNT]
                    [--paranoid SHOULD IT BREAK ON UNHANDLED EXCEPTIONS?]

    Elevator command line manager

    optional arguments:
        -h, --help    show this help message and exit
        --daemon      Launch elevator as a daemon
        --config      Path to elevator server config file, eventually
        --bind        Ip to bind server to
        --port        Port the server should listen on
        --workers     How many workers should be spawned (Threads
                      with concurrent access to all the db store)
        --paranoid    If option is set, Elevator will shutdown
                      and log on first unhandled exception
