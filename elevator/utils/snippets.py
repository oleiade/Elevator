#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Lambda function which tranforms a ConfigParser items
# list of tuples object into a dictionnary
items_to_dict = lambda items: {k: v for k, v in items}


# Iterates through a sequence of size `clen`
chunks = lambda seq, clen: [seq[i: (i + clen)] \
                            for i in xrange(0, len(seq), clen)]


# Decodes a list content from a given charset
ldecode = lambda list, charset: [string.decode(charset) for string in charset]

# Encodes a list content from a given charset
lencode = lambda list, charset: [string.encode(charset) for string in charset]


# Checks if a sequence is ascendently sorted
asc_sorted = lambda seq: all(seq[i] <= seq[i + 1] \
                             for i in xrange(len(seq) - 1))

# idem descending
desc_sorted = lambda seq: all(seq[i] >= seq[i + 1] \
                              for i in xrange(len(seq) - 1))
