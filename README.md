# Elevator

[![Build Status](https://secure.travis-ci.org/oleiade/Elevator.png)](http://travis-ci.org/oleiade/Elevator)

Key-Value store written in Python and based on levelDB, allows high performance on-disk bulk read/write.

Allows async, multithreaded and/or remote access to a multi-leveldb backend.

Relying on the zeromq network library and msgpack serialization format, it is made to be portable between languages and
platforms.

See [Documentation](http://oleiade.github.com/Elevator) for more details


### Depends on

- zmq
- pyzmq
- leveldb
- py-leveldb


### Installation


```bash
$ pip install fabric
$ fab build
$ python setup.py install
```


### Usage

When elevator is installed, you can then launch the server using the elevator executable.
Note that a --daemon option is disposable, and allows you to run elevator server as a daemon,
storing it's pid in .pid file in /tmp.

See config/elevator.conf for an example of Elevator configuration.

*Example*:

```bash
$ elevator --help
usage: elevator [-h] [--daemon] [--config CONFIG FILE] [--bind BIND] [--port PORT]
                [--workers WORKERS COUNT] [--paranoid SHOULD IT BREAK ON UNHANDLED EXCEPTIONS?]

Elevator command line manager

optional arguments:
    -h, --help       show this help message and exit
    --daemon      Launch elevator as a daemon
    --config      Path to elevator server config file, eventually
    --bind        Ip to bind server to
    --port        Port the server should listen on
    --workers     How many workers should be spawned (Threads with concurrent access to all the db store)
    --paranoid    If option is set, Elevator will shutdown and log on first unhandled exception
```

### Clients

*Python* : [py-elevator] (http://github.com/oleiade/py-elevator)

*Clojure* : *Coming soon*

*C* : *Coming soon*


### Thanks

Thanks to [srinikom](https://github.com/srinikom) for its [leveldb-server](https://github.com/srinikom/leveldb-server) which was a very good base to start from.
