import unittest
from ot import Add, Client

class CaptureCallToReceive(object):
    def __init__(self, remote):
        self.remote = remote
        self.argss = []

    def receive(self, *args):
        self.argss.append(args)

    def call(self):
        for args in self.argss:
            self.remote.receive(*args)
        self.argss = []

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

    def test_multiple_concurrent_pending_message_are_reverted(self):
        client1 = Client()
        client2 = Client()

        remote1 = CaptureCallToReceive(client1)
        remote2 = CaptureCallToReceive(client2)

        client1.add_remote(remote2)
        client2.add_remote(remote1)

        client1.generate(Add(0, 'x'))
        client1.generate(Add(1, 'y'))

        client2.generate(Add(0, 'o'))

        self.assertEquals(client1.data, ['x', 'y'])
        self.assertEquals(client2.data, ['o'])

        remote1.call()
        remote2.call()

        self.assertEquals(client1.data, [])
        self.assertEquals(client2.data, [])

    def test_multiple_pending_messages_are_applied(self):
        client1 = Client()
        client2 = Client()

        remote1 = CaptureCallToReceive(client1)
        remote2 = CaptureCallToReceive(client2)

        client1.add_remote(remote2)
        client2.add_remote(remote1)

        client1.generate(Add(0, 'x'))
        client1.generate(Add(1, 'y'))

        remote1.call()
        remote2.call()

        client2.generate(Add(0, 'o'))

        remote1.call()
        remote2.call()

        self.assertEquals(client1.data, ['o', 'x', 'y'])
        self.assertEquals(client2.data, ['o', 'x', 'y'])
