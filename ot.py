class Add(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

    def apply(self, data):
        data.insert(self.position, self.value)

class Client(object):
    def __init__(self):
        self.data = []

    def generate(self, operation):
        operation.apply(self.data)
