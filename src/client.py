import asyncio
import socketio
import argparse
import time
import json
import sys

from transport_message import TransportMessage
from services import Services

class Client:

    def __init__(self, server_id) -> None:
        self.socket = socketio.Client()
        self.socket.connect(server_id)
        self.socket.on("PRINT_MESSAGE", self._handleResponse)

    def subscribe(self, topics):
        if not isinstance(topics, list):
            topics = [topics]

        for t in topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=t)
            self.socket.emit("SUBSCRIBE_TOPIC", tMessage.json())

    def unsubscribe(self, topics):
        if not isinstance(topics, list):
            topics = [topics]

        for t in topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=t)
            self.socket.emit("UNSUBSCRIBE_TOPIC", tMessage.json())

    def publish(self, topic, message):
        tMessage = TransportMessage(timestamp=time.time(), topic=topic, payload=message)
        self.socket.emit("PUBLISH_TOPIC", tMessage.json())

    def listTopics(self):
        tMessage = TransportMessage(timestamp=time.time())
        self.socket.emit("LIST_TOPICS", tMessage.json())

    def getTopicStatus(self, topic):
        tMessage = TransportMessage(timestamp=time.time(), topic=topic)
        self.socket.emit("GET_TOPIC_STATUS", tMessage.json())

    # @socket.on("PRINT_MESSAGE")
    def _handleResponse(self, response):
        print(f"SERVER RESPONSE: {self, response}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Client",
        description="Client for Publisher"
    )

    parser.add_argument("-sub", "--subscribe", nargs="+", help="list of topics to subscribe", metavar="TOPIC")
    parser.add_argument("-p", "--publish", help="published topic", metavar="TOPIC")
    parser.add_argument("-m", "--message", help="message to be published to topic", metavar="STRING")
    parser.add_argument("-l", "--list", action="store_true", help="get all list topics from server")
    parser.add_argument("-st", "--status", action="store_true", help="get topic status from server")
    parser.add_argument("-s", "--server", required=True, help="server address", metavar="ADDRESS:PORT")

    args = parser.parse_args()

    # call client functions
    cli = Client(args.server)

    if args.subscribe:
        try:
            cli.subscribe(args.subscribe)
        except KeyboardInterrupt: # Catch Ctrl+C TODO: use exit handler
            cli.unsubscribe(args.subscribe)
            sys.exit()

    elif args.publish and args.message:
        cli.publish(args.publish, args.subscribe)

    elif args.list:
        cli.listTopics(args.list)
    
    elif args.status:
        cli.listTopics(args.status)

    else:
        print("No action, please check your parameters")
    
    sys.exit()

