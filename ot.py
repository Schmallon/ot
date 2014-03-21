def xform(operation1, operation2):
    return operation2.reverted(), operation1.reverted()

class Remove(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

    def apply(self, data):
        assert data[self.position] == self.value
        data.pop(self.position)

    def reverted(self):
        return Add(self.position, self.value)

class Add(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

    def apply(self, data):
        data.insert(self.position, self.value)

    def reverted(self):
        return Remove(self.position, self.value)

class Client(object):
    def __init__(self):
        self.data = []
        self.remotes = []
        self.num_sent_messages = 0
        self.num_received_messages = 0
        self.sent_messages = []

    def generate(self, operation):
        operation.apply(self.data)
        self.send(operation)
        self.sent_messages.append(operation)
        self.num_sent_messages += 1

    def add_remote(self, remote):
        self.remotes.append(remote)

    def send(self, operation):
        for remote in self.remotes:
            remote.receive(operation, self.num_sent_messages, self.num_received_messages)

    def receive(self, operation, num_sent_messages, num_received_messages):
        assert self.num_received_messages == num_sent_messages
        for i, message in enumerate(self.sent_messages):
            operation, self.sent_messages[i] = xform(operation, message)
        operation.apply(self.data)
        self.num_received_messages += 1
