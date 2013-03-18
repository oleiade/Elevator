
0.5c / 2013-03-18
==================

  * Fix : DatabaseStore last acess property
  * Fix: init script creates pid file
  * Fix: pyzmq version
  * Fix: explicit daemon init failures

0.5 / 2013-02-01
==================

  * Remove: legacy setup_loggers function
  * fix #123: exposing a database object
  * ref #123: Renamed DatabasesHandler to DatabaseStore
  * Fix: elevator benchmarks
  * Fix: supervisor test should remove their tests files
  * Add: tests for backend atm
  * Add: backend supervisor tests + fixes
  * update: enhance backend majordome management
  * fix #125: backend does not instantiate it's own DatabasesHandler anymore
  * Fix: elevator tests fakers now uses a clear files/dirs pattern
  * Update: more obvious DatabaseHandler args names
  * Add: benchmarks using hurdles and pyelevator
  * update #120 : Auto re-mount unmounted database on new requests
  * Fix : backend properly tears down workers
  * fix #120, fix #91: Implement Majordom watcher thread
  * Update #120: set databases last access marker
  * Update 120: move ocd worker to backend module
  * Update #121: implement last activity action on workers
  * Update #121: Documented worker
  * Update #121: Workers poll to reduce cpu usage + backend refactoring
  * Update #121: use an internal message protocol between supervisor and workers
  * Update: Moved the backend elements in their own module
  * Fix #122: workers now set their processing state
  * Refactor: moved loggers init in their own log module
  * Update #121: fixed workers stop action
  * Update #121: Added constants to normalize interaction with workers
  * Add #121: basic workers supervisor implementation, implies a lot of refactoring
  * Update: rename server poller
  * Update: use ROUTER/DEALER terminology and rename workerpool and proxy to backend and frontend
  * Update: renamed conf module to args

0.4b / 2013-01-28
==================

  * Fix: Refactor api tests
  * Fix #119: Range and Slice now support include_key, and include_value params
  * Remove: max cache management + Add: Lru cache and bloom filters

0.4a / 2013-01-22
==================

  * Add : Implement PING command
  * Add : Cli module
  * Add : Debian packaging files
  * Update: Use plyvel leveldb backend
  * Update: Use plyvel bloom filter in read operations
  * Update: Add experimental command line doc
  * Update: Set fabfile as a module
  * Update: Documentation to fit with plyvel
  * Update #114: Run MGet against db snapshot
  * Update : working cmdline
  * Fix #114: Enhance MGET perfs by acting on a min/max keys range slice
  * Fix #113: handle MGET arguments in command line
  * Many other little updates and fixes, see logs


0.4 / 2012-10-22
==================

  * Add: restore theme
  * Add : Base sphinx documentation
  * Update : new License MIT
  * Fix #86: IOError when bad config file supplied as cmdline argument
  * Fix #95: Elevator will start and log errors even though some databases are corrupted
  * Fix : log-level debug messages format
  * Fix : travis, tests, requirements

0.3d / 2012-10-19
==================

  * Add : Request error for invalid request messages
  * Update #91: Mount default at server startup
  * Update #91: Mount/Unmount command + auto-mount on connect
  * Update #91: add a ticker class, which executes a function every x seconds
  * Update #30, Update #99: Compress Responses on demande (request.meta['compression'])
  * Update #88, Update #99: now responses comes in two parts header+content
  * Update #88: Fix MGet, Range, Slice return values types to suite with new responses format
  * Update #88: Refactored Request/Responses format
  * Update : Refactored DatabasesHandler internal storage
  * Update : Few refactoring on loggers handling
  * Update : Refactored DBConnect no more db_uid to provide in request
  * Fix #97: provide mono-letters args
  * Fix #89: Log requests/responses on log-level=DEBUG
  * Fix #87: Refactored logging
  * Fix #100: Non blocking workers, graceful shutdown == PERFORMANCES
  * Fix #98: Activity logging on both file and stdout
  * Fix #101: fixed ipc handling
  * Fix : api tests for compatibility with new Req/Resp
  * Fix : refactored tests for new Range/Slice behavior when size == 1
  * Fix : Mount/Unmount passed args

