import unittest
from ot import Add, Client
import Queue

class Remotes(object):
    def __init__(self):
        self.remotes = []

    def call(self):
        for remote in self.remotes:
            remote.call()

    def create(self, remote):
        capturing_remote = CaptureCallToReceive(remote)
        self.remotes.append(capturing_remote)
        return capturing_remote

class ServerAndTwoClients(object):
    def __init__(self):
        self.remotes = Remotes()

        self.server = Client()
        self.client1 = Client()
        self.client2 = Client()

        self.remote_server = self.remotes.create(self.server)
        self.remote_client1 = self.remotes.create(self.client1)
        self.remote_client2 = self.remotes.create(self.client2)

        self.server.add_remote(self.remote_client1)
        self.server.add_remote(self.remote_client2)
        self.client1.add_remote(self.remote_server)
        self.client2.add_remote(self.remote_server)


class CaptureCallToReceive(object):
    def __init__(self, remote):
        self.remote = remote
        self.args_queue = Queue.Queue()

    def receive(self, *args):
        self.args_queue.put(args)

    def call(self):
        try:
            while True:
                args = self.args_queue.get_nowait()
                self.remote.receive(*args)
        except Queue.Empty:
            pass

    def id(self):
        return self.remote.id()

class TestTransform(unittest.TestCase):
    def test_generating_operation_changes_data(self):
        client = Client()
        client.generate(Add(0, 'x'))
        self.assertEquals(client.data, ['x'])

    def test_connected_client_updates(self):
        client1 = Client()
        client2 = Client()
        client1.add_remote(client2)
        client2.add_remote(client1)

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

    def test_operations_are_forwarded_to_multiple_clients(self):
        f = ServerAndTwoClients()

        f.client1.generate(Add(0, 'x'))
        f.client1.generate(Add(1, 'y'))
        f.remotes.call()
        f.remotes.call()

        self.assertEquals(f.client1.data, ['x', 'y'])
        self.assertEquals(f.client2.data, ['x', 'y'])

        f.client2.generate(Add(0, 'o'))
        f.remotes.call()
        f.remotes.call()

        self.assertEquals(f.client1.data, ['o', 'x', 'y'])
        self.assertEquals(f.client2.data, ['o', 'x', 'y'])

    def test_conflicting_adds_are_reverted_with_server(self):
        f = ServerAndTwoClients()

        f.client1.generate(Add(0, 'x'))
        f.client2.generate(Add(0, 'y'))

        self.assertEquals(f.client1.data, ['x'])
        self.assertEquals(f.client2.data, ['y'])

        f.remotes.call()
        f.remotes.call()
        f.remotes.call()
        f.remotes.call()

        self.assertEquals(f.client1.data, [])
        self.assertEquals(f.client2.data, [])
