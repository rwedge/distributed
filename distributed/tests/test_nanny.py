from distributed import Nanny, Center, rpc
from distributed.utils_test import loop

from tornado.tcpclient import TCPClient
from tornado import gen

def test_metadata(loop):
    c = Center('127.0.0.1', 8006)
    n = Nanny('127.0.0.1', 8007, 8008, '127.0.0.1', 8006, ncores=2)
    c.listen(8006)

    @gen.coroutine
    def f():
        nn = rpc(ip=n.ip, port=n.port)
        yield n._start()
        assert n.process.is_alive()
        assert c.ncores[n.worker_address] == 2
        assert c.nannies[n.worker_address] > 8000

        yield nn.kill()
        assert n.worker_address not in c.ncores
        assert n.worker_address not in c.nannies
        assert not n.process

        yield nn.kill()
        assert n.worker_address not in c.ncores
        assert n.worker_address not in c.nannies
        assert not n.process

        yield nn.instantiate()
        assert n.process.is_alive()
        assert c.ncores[n.worker_address] == 2
        assert c.nannies[n.worker_address] > 8000

        yield nn.terminate()
        assert not n.process

        if n.process:
            n.process.terminate()

    loop.run_sync(f)
