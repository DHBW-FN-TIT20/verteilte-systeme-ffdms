
class TransportMessage:

    def __init__(self, timestamp, topic = None, payload = None) -> None:
        self.timestamp = timestamp
        self.topic = topic
        self.payload = payload
