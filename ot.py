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
        self.sent_messages = []
        self.num_sent_messages = 0
        self.num_received_messages = 0

    def generate(self, operation):
        operation.apply(self.data)
        self.send(operation)
        self.sent_messages.append(operation)
        self.num_sent_messages += 1

    def add_remote(self, remote):
        self.remotes.append(remote)

    def send(self, operation):
        for remote in self.remotes:
            remote.receive(operation, self.num_received_messages)

    def receive(self, operation, num_received_messages):
        if self.num_sent_messages > num_received_messages:
            for message in reversed(self.sent_messages):
                message.reverted().apply(self.data)
            self.sent_messages = []
        else:
            operation.apply(self.data)
        self.num_received_messages += 1
