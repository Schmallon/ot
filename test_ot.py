import unittest
from ot import Add, Client

class CaptureCallToReceive(object):
    def __init__(self, remote):
        self.remote = remote
        self.args = None

    def receive(self, *args):
        assert self.args == None
        self.args = args

    def call(self):
        self.remote.receive(*self.args)

class TestTransform(unittest.TestCase):
    def test_generating_operation_changes_data(self):
        client = Client()
        client.generate(Add(0, 'x'))
        self.assertEquals(client.data, ['x'])

    def test_connected_client_updates(self):
        client1 = Client()
        client2 = Client()
        client1.add_remote(client2)

        client1.generate(Add(0, 'x'))

        self.assertEquals(client1.data, ['x'])
        self.assertEquals(client2.data, ['x'])

    def test_conflicting_adds_are_reverted(self):
        client1 = Client()
        client2 = Client()

        remote1 = CaptureCallToReceive(client1)
        remote2 = CaptureCallToReceive(client2)

        client1.add_remote(remote2)
        client2.add_remote(remote1)

        client1.generate(Add(0, 'x'))
        client2.generate(Add(0, 'y'))

        self.assertEquals(client1.data, ['x'])
        self.assertEquals(client2.data, ['y'])

        remote1.call()
        remote2.call()

        self.assertEquals(client1.data, [])
        self.assertEquals(client2.data, [])
