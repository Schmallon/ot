class Add(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

    def apply(self, data):
        data.insert(self.position, self.value)

class Client(object):
    def __init__(self):
        self.data = []
        self.remotes = []

    def generate(self, operation):
        operation.apply(self.data)
        self.send(operation)

    def add_remote(self, remote):
        self.remotes.append(remote)

    def send(self, operation):
        for remote in self.remotes:
            remote.receive(operation)

    def receive(self, operation):
        operation.apply(self.data)
