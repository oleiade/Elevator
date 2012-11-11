# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import sys
import zmq

from .io import prompt, parse_input, output_result
from .client import send_cmd
from .args import init_parser


in_stream = sys.stdin
out_stream = sys.stdout
err_stream = sys.stderr

timeout = 10000
context = zmq.Context()
socket = context.socket(zmq.XREQ)


def main():
    global socket
    global timeout

    args = init_parser().parse_args(sys.argv[1:])

    host = "%s://%s" % (args.transport, args.endpoint)
    socket.setsockopt(zmq.RCVTIMEO, timeout)
    socket.connect(host)

    while True:
        input_str = prompt()
        command = parse_input(input_str)
        # result = send_cmd(command)
        # output_result(result)


if __name__ == "__main__":
    main()
