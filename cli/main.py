# -*- coding: utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

from __future__ import absolute_import

import sys

from .io import prompt, parse_input, output_result
from .client import Client
from .args import init_parser


in_stream = sys.stdin
out_stream = sys.stdout
err_stream = sys.stderr


def main():
    args = init_parser().parse_args(sys.argv[1:])
    client = Client(protocol=args.protocol,
                    endpoint=args.endpoint)

    try:
        while True:
            input_str = prompt()

            if input_str:
                command, args = parse_input(input_str)

                if not command == "DBCONNECT":
                    result = client.send_cmd(client.db_uid, command, args)
                    output_result(result)
                else:
                    client.connect(*args)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
