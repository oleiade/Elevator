# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import zmq
import logging

errors_logger = logging.getLogger("errors_logger")


class Frontend():
    def __init__(self, config):
        self.config = config
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)

        endpoint = ':'.join([self.config['bind'], self.config['port']])
        self.host = self._gen_bind_adress(self.config['transport'], endpoint)
        self.socket.bind(self.host)

    def __del__(self):
        self.socket.close()
        self.context.term()

    def _gen_bind_adress(self, transport, endpoint):
        if transport == 'ipc':
            if not 'unixsocket' in self.config:
                err_msg = "Ipc transport layer was selected, but no unixsocket "\
                          "path could be found in conf file"
                errors_logger.exception(err_msg)
                raise KeyError(err_msg)
            return '{0}://{1}'.format(transport, self.config['unixsocket'])

        else:  # consider it's tcp
            return '{0}://{1}'.format(transport, endpoint)
