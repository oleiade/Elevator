# Copyright 2013 by Eric Suh
# Copyright (c) 2013 Theo Crevon
# This code is freely licensed under the MIT license found at
# <http://opensource.org/licenses/MIT>

import sys
import os
import errno
import atexit
import signal
import time
import subprocess

from contextlib import contextmanager


class PIDFileError(Exception):
    pass


@contextmanager
def pidfile(path, pid):
    make_pidfile(path, pid)
    yield
    remove_pidfile(path)


def readpid(path):
    with open(path) as f:
        pid = f.read().strip()
    if not pid.isdigit():
        raise PIDFileError('Malformed PID file at path {}'.format(path))
    return pid


def pidfile_is_stale(path):
    '''Checks if a PID file already exists there, and if it is, whether it
    is stale. Returns True if a PID file exists containing a PID for a
    process that does not exist any longer.'''
    try:
        pid = readpid(path)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return False # nonexistant file isn't stale
        raise e
    if pid == '' or not pid.isdigit():
        raise PIDFileError('Malformed PID file at path {}'.format(path))
    return not is_pid_running(pid)


def _ps():
    raw = subprocess.check_output(['ps', '-eo', 'pid'])
    return [line.strip() for line in raw.split('\n')[1:] if line != '']


def is_pid_running(pid):
    try:
        procs = os.listdir('/proc')
    except OSError as e:
        if e.errno == errno.ENOENT:
            return str(pid) in _ps()
        raise e
    return str(pid) in [proc for proc in procs if proc.isdigit()]


def make_pidfile(path, pid):
    '''Create a PID file. '''
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except OSError as e:
        if e.errno == errno.EEXIST:
            if pidfile_is_stale(path):
                remove_pidfile(path)
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            else:
                raise PIDFileError(
                    'Non-stale PID file already exists at {}'.format(path))

    pidf = os.fdopen(fd, 'w')
    pidf.write(str(pid))
    pidf.flush()
    pidf.close()


def remove_pidfile(path):
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


class daemon(object):
    'Context manager for POSIX daemon processes'

    def __init__(self,
                 pidfile=None,
                 workingdir='/',
                 umask=0,
                 stdin=None,
                 stdout=None,
                 stderr=None,
                ):
        self.pidfile = pidfile
        self.workingdir = workingdir
        self.umask = umask

        devnull = os.open(os.devnull, os.O_RDWR)
        self.stdin = stdin.fileno() if stdin is not None else devnull
        self.stdout = stdout.fileno() if stdout is not None else devnull
        self.stderr = stderr.fileno() if stderr is not None else self.stdout

    def __enter__(self):
        self.daemonize()
        return

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
        return

    def daemonize(self):
        '''Set up a daemon.

        There are a few major steps:
        1. Changing to a working directory that won't go away
        2. Changing user permissions mask
        3. Forking twice to detach from terminal and become new process leader
        4. Redirecting standard input/output
        5. Creating a PID file'''

        # Set up process conditions
        os.chdir(self.workingdir)
        os.umask(self.umask)

        # Double fork to daemonize
        _getchildfork(1)
        os.setsid()
        _getchildfork(2)

        # Redirect standard input/output files
        sys.stdin.flush()
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(self.stdin, sys.stdin.fileno())
        os.dup2(self.stdout, sys.stdout.fileno())
        os.dup2(self.stderr, sys.stderr.fileno())

        # Create PID file
        if self.pidfile is not None:
            pid = str(os.getpid())
            try:
                make_pidfile(self.pidfile, pid)
            except PIDFileError as e:
                sys.stederr.write('Creating PID file failed. ({})'.format(e))
                os._exit(os.EX_OSERR)
        atexit.register(self.stop)

    def stop(self):
        if self.pidfile is not None:
            pid = readpid(self.pidfile)
            try:
                while True:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    remove_pidfile(self.pidfile)
                else:
                    raise

def _getchildfork(n):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(os.EX_OK) # Exit in parent
    except OSError as e:
        sys.stederr.write('Fork #{} failed: {} ({})\n'.format(
            n, e.errno, e.strerror))
        os._exit(os.EX_OSERR)
