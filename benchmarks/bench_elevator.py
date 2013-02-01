import uuid
import hurdles

from hurdles.tools import extra_setup

from pyelevator import Elevator, WriteBatch


class BenchElevator(hurdles.BenchCase):
    def setUp(self):
        self.client = Elevator(timeout=10)
        self._bootstrap_db()

    def tearDown(self):
        pass

    def _bootstrap_db(self):
        with WriteBatch(timeout=10000) as batch:
            for x in xrange(100000):
                batch.Put(str(x), uuid.uuid4().hex)

    @extra_setup("import uuid\n"
                 "from pyelevator import WriteBatch\n"
                 "batch = WriteBatch(timeout=1000)\n"
                 "for x in xrange(100000):\n"
                 "    batch.Put(str(x), uuid.uuid4().hex)")
    def bench_write_batch(self, *args, **kwargs):
        kwargs['batch'].Write()

    @extra_setup("import random\n"
                 "keys = [str(random.randint(1, 9999)) for x in xrange(9999)]")
    def bench_mget_on_random_keys(self, *args, **kwargs):
        self.client.MGet(kwargs['keys'])

    @extra_setup("import random\n"
                 "keys = [str(random.randint(1, 9999)) for x in xrange(9999)]")
    def bench_mget_on_random_keys_with_compression(self, *args, **kwargs):
        self.client.MGet(kwargs['keys'], compression=True)

    @extra_setup("keys = [str(x) for x in xrange(9999)]")
    def bench_mget_on_serial_keys(self, *args, **kwargs):
        self.client.MGet(kwargs['keys'])

    @extra_setup("keys = [str(x) for x in xrange(9999)]")
    def bench_mget_on_serial_keys_with_compression(self, *args, **kwargs):
        self.client.MGet(kwargs['keys'], compression=True)

    def bench_range(self, *args, **kwargs):
        self.client.Range('1', '999998')

    def bench_range_with_compression(self, *args, **kwargs):
        self.client.Range('1', '999998', compression=True)

    def bench_slice(self, *args, **kwargs):
        self.client.Slice('1', 999998)

    def bench_slice_with_compression(self, *args, **kwargs):
        self.client.Slice('1', 999998, compression=True)

    @extra_setup("import random\n"
                 "keys = [str(random.randint(1, 10)) for x in xrange(10)]")
    def bench_random_get(self, *args, **kwargs):
        for key in kwargs['keys']:
            self.client.Get(key)

    def bench_serial_get(self, *args, **kwargs):
        pos = 1
        limit = 10

        while pos <= limit:
            self.client.Get(str(pos))
            pos += 1
