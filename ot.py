from operations import Noop, Compose, Reverted

class Session(object):
    def __init__(self, remote):
        self.remote =remote
        self.num_sent_messages = 0
        self.num_received_messages = 0
        self.sent_messages = []

    def remove_processed_messages(self, num_received_messages):
        self.sent_messages = [(num, message)
            for (num, message) in self.sent_messages
            if num >= num_received_messages]

    def transform_operation(self, operation):
        if self.sent_messages:
            result = Reverted(Compose([op for (num, op) in self.sent_messages]))
            self.sent_messages = [(self.num_sent_messages - 1, Noop())]
            return result
        else:
            return operation

    def send(self, operation, sending_remote_id):
        self.remote.send_message(sending_remote_id, operation, self.num_received_messages)
        self.sent_messages.append([self.num_sent_messages, operation])
        self.num_sent_messages += 1

class Client(object):
    def __init__(self):
        self.data = []
        self.sessions = {}

    def client_id(self):
        return self

    def add_remote(self, remote):
        self.sessions[remote.client_id()] = Session(remote)

    def generate(self, operation):
        operation.apply(self.data)
        for session in self.sessions.values():
            session.send(operation, self.client_id())

    def receive(self, sending_remote_id, operation, num_received_messages):
        session = self.sessions[sending_remote_id]
        session.remove_processed_messages(num_received_messages)

        operation = session.transform_operation(operation)
        operation.apply(self.data)

        self._send_to_other_sessions(sending_remote_id, operation)
        session.num_received_messages += 1

    def _send_to_other_sessions(self, sending_remote_id, operation):
        for id, other_session in self.sessions.iteritems():
            if id != sending_remote_id:
                other_session.send(operation, self.client_id())
