
class TransportMessage:

    def __init__(self, serviceId, timestamp, payload = None) -> None:
        self.serviceId = serviceId
        self.timestamp = timestamp
        self.payload = payload