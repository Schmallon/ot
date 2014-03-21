def xform(a, b):
    return b.reverted(), a.reverted()

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

class Session(object):
    def __init__(self, remote):
        self.remote =remote
        self.num_sent_messages = 0
        self.num_received_messages = 0
        self.sent_messages = []

class Client(object):
    def __init__(self):
        self.data = []
        self.sessions = {}

    def generate(self, operation):
        operation.apply(self.data)
        self.send(operation)

    def id(self):
        return self

    def add_remote(self, remote):
        self.sessions[remote.id()] = Session(remote)

    def send(self, operation):
        for session in self.sessions.values():
            self.send_to_session(session, operation)

    def send_to_session(self, session, operation):
            session.remote.receive(self.id(), operation, session.num_received_messages)
            session.sent_messages.append([session.num_sent_messages, operation])
            session.num_sent_messages += 1

    def receive(self, sending_remote_id, operation, num_received_messages):
        #import pdb; pdb.set_trace()
        #print self.id()
        #print operation, operation.value
        #print

        session = self.sessions[sending_remote_id]

        session.sent_messages = [(num, message)
                for (num, message) in session.sent_messages
                if num >= num_received_messages]

        for i, (num, message) in enumerate(session.sent_messages):
            operation, session.sent_messages[i] = xform(operation, message)

        operation.appy(self.data)

        #if session.num_sent_messages > num_received_messages:
            #for num, message in reversed(session.sent_messages):
                #message.reverted().apply(self.data)
            #session.sent_messages = []
        #else:
            #operation.apply(self.data)

        for id, session in self.sessions.iteritems():
            if id != sending_remote_id:
                self.send_to_session(session, operation)

        session.num_received_messages += 1

