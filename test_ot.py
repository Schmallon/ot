import unittest
from ot import Add, Client

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

