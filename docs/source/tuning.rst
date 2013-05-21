.. _tuning:

======
Tuning
======

.. _Storage_engine_options:

Storage engine options
======================

The Elevator storage engine can be configured to fit with your dataset size and problematics through the configuration file ``[storage_engine]`` section. There you can set options which will be used to create and mount the underlying storage of your databases.

.. _write_buffer_size:

Write Buffer Size
-----------------

Larger write buffers increase performance, especially during bulk loads. Up to two write buffers may be held in memory at the same time, so you may wish to adjust this parameter to control memory usage.

Default : ``write_buffer_size``: 67108864 (64M)


.. _max_open_files:

Max Open Files
--------------

Number of open files that can be used by the DB. You may need to increase this if your database has a large working set.

Default: ``max_open_files``: 150


.. _block_size:

Block Size
----------

Approximate size of user data packed per block. For very large databases bigger block sizes are likely to perform better so increasing the block size to 256k (or another power of 2) may be a good idea. Keep in mind that LevelDB's default internal block cache is only 8MB so if you increase the block size you will want to resize cache_size as well.

Default: ``block_size``: 131072 (128K)


.. _cache_size:

Cache Size
----------

The cache_size determines how much data LevelDB caches in memory. The more of your data set that can fit in-memory, the better LevelDB will perform. The LevelDB cache works in conjunction with your operating system and file system caches; do not disable or under-size them. LevelDB keeps keys and values in a block cache, this allows for management of key spaces that are larger than available memory.

Default: ``cache_size``: 536870912 (512MB)

.. _bloom_filter_bits:

Bloom filter bits
-----------------

Bloom filter will reduce the number of unnecessary disk reads needed for Get() calls by a factor of approximately a 100. Increasing the bits per key will lead to a larger reduction at the cost of more memory usage.

Default: ``bloom_filter_bits``: 100

.. _verify_checksum:

Verify Checksums
----------------

If true, all data read from underlying storage will be verified against corresponding checksums.

Default: ``verify_checksum``: false



.. _about_leveldb:

About Leveldb
=============

(Full credit for this whole section goes to `Riak <http://docs.basho.com/riak/latest/tutorials/choosing-a-backend/LevelDB/#LevelDB-Implementation-Details>`_ which made a great work describing how the leveldb engine works)

`LevelDB <http://code.google.com/p/leveldb/>`_ is a Google sponsored open source project that has been incorporated into Elevator for storage of key/value information on disk. The implementation of LevelDB is similar in spirit to the representation of a single Bigtable tablet (section 5.3).


How “Levels” Are Managed
------------------------

LevelDB is a memtable/sstable design. The set of sorted tables are organized into a sequence of levels. Each level stores approximately ten times as much data as the level before it. The sorted table generated from a flush is placed in a special young level (also called level-0). When the number of young files exceeds a certain threshold (currently four), all of the young files are merged together with all of the overlapping level-1 files to produce a sequence of new level-1 files (a new level-1 file is created for every 2MB of data.)

Files in the young level may contain overlapping keys. However files in other levels have distinct non-overlapping key ranges. Consider level number L where L >= 1. When the combined size of files in level-L exceeds (10^L) MB (i.e. 10MB for level-1, 100MB for level-2, …), one file in level-L, and all of the overlapping files in level-(L+1) are merged to form a set of new files for level-(L+1). These merges have the effect of gradually migrating new updates from the young level to the largest level using only bulk reads and writes (i.e., minimizing expensive disk seeks).

When the size of level L exceeds its limit, LevelDB will compact it in a background thread. The compaction picks a file from level L and all overlapping files from the next level L+1. Note that if a level-L file overlaps only part of a level-(L+1) file, the entire file at level-(L+1) is used as an input to the compaction and will be discarded after the compaction. Compactions from level-0 to level-1 are treated specially because level-0 is special (files in it may overlap each other). A level-0 compaction may pick more than one level-0 file in case some of these files overlap each other.

A compaction merges the contents of the picked files to produce a sequence of level-(L+1) files. LevelDB will switch to producing a new level-(L+1) file after the current output file has reached the target file size (2MB). LevelDB will also switch to a new output file when the key range of the current output file has grown enough to overlap more then ten level-(L+2) files. This last rule ensures that a later compaction of a level-(L+1) file will not pick up too much data from level-(L+2).

Compactions for a particular level rotate through the key space. In more detail, for each level L, LevelDB remembers the ending key of the last compaction at level L. The next compaction for level L will pick the first file that starts after this key (wrapping around to the beginning of the key space if there is no such file).

Level-0 compactions will read up to four 1MB files from level-0, and at worst all the level-1 files (10MB) (i.e., LevelDB will read 14MB and write 14MB in that case).

Other than the special level-0 compactions, LevelDB will pick one 2MB file from level L. In the worst case, this will overlap with approximately 12 files from level L+1 (10 because level-(L+1) is ten times the size of level-L, and another two at the boundaries since the file ranges at level-L will usually not be aligned with the file ranges at level-L+1). The compaction will therefore read 26MB, write 26MB. Assuming a disk IO rate of 100MB/s, the worst compaction cost will be approximately 0.5 second.

If we throttle the background writing to a reasonably slow rate, for instance 10% of the full 100MB/s speed, a compaction may take up to 5 seconds. If the user is writing at 10MB/s, LevelDB might build up lots of level-0 files (~50 to hold the 5*10MB). This may significantly increase the cost of reads due to the overhead of merging more files together on every read.

Compaction
----------

Levels are compacted into ordered data files over time. Compaction first computes a score for each level as the ratio of bytes in that level to desired bytes. For level 0, it computes files / desired files instead. The level with the highest score is compacted.

When compacting L0 the only special case to consider is that after picking the primary L0 file to compact, it will check other L0 files to determine the degree to which they overlap. This is an attempt to avoid some I/O, we can expect L0 compactions to usually if not always be “all L0 files”.

See the PickCompaction routine in 1 for all the details.