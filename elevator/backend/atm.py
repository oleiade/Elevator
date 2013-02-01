# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import threading
import logging
import time


activity_logger = logging.getLogger("activity_logger")


class Majordome(threading.Thread):
    """Ticks every `interval` minutes and unmounts unused databases
    since last tick.

    Inspired of : http://pastebin.com/xNV7hx8h"""
    def __init__(self, supervisor, db_handler, interval, iterations=0):
        threading.Thread.__init__(self)
        self.interval = interval * 60  # Turn it's value in minutes
        self.last_tick = time.time()
        self.iterations = iterations
        self.supervisor = supervisor
        self.db_handler = db_handler
        self.function = self.unmount_unused_db
        self.finished = threading.Event()

    def unmount_unused_db(self):
        """Automatically unmount unused databases on tick"""
        db_last_access = self.db_handler.last_access

        for db, access in db_last_access.iteritems():
            if (access < self.last_tick):
                db_status = self.db_handler[db]['status']
                if db_status == self.db_handler.STATUSES.MOUNTED:
                    self.db_handler.umount(self.db_handler[db]['name'])
                    activity_logger.debug("No activity on {db}, unmouting...".format(db=db))

    def run(self):
        count = 0

        while (not self.finished.is_set() and
               (self.iterations <= 0 or count < self.iterations)):
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function()
                self.last_tick = time.time()
                count += 1

    def cancel(self):
        self.finished.set()
