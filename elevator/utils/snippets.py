#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Checks if a str is a word(unique),
# or an expression (more than one word).
is_expression = lambda s: ' ' in s.strip()


# Lambda function which tranforms a ConfigParser items
# list of tuples object into a dictionnary,
# doesn't use dict comprehension in order to keep 2.6
# backward compatibility.
def items_to_dict(items):
    res = {}

    for k, v in items:
        res[k] = v
    return res

# Iterates through a sequence of size `clen`
chunks = lambda seq, clen: [seq[i:(i + clen)] for i in xrange(0, len(seq), clen)]

# Decodes a list content from a given charset
ldecode = lambda list, charset: [string.decode(charset) for string in charset]

# Encodes a list content from a given charset
lencode = lambda list, charset: [string.encode(charset) for string in charset]

# Checks if a sequence is ascendently sorted
asc_sorted = lambda seq: all(seq[i] <= seq[i + 1] for i in xrange(len(seq) - 1))

# idem descending
desc_sorted = lambda seq: all(seq[i] >= seq[i + 1] for i in xrange(len(seq) - 1))

# Convert bytes to Mo
from_bytes_to_mo = lambda bytes: bytes / 1048576

#Convert Mo to bytes
from_mo_to_bytes = lambda mo: mo * 1048576

# Convert seconds to milliseconds
sec_to_ms = lambda s: s * 1000
