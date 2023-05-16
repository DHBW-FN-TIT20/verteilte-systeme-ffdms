import asyncio
import socketio
import argparse
import time
import json
import sys

from transport_message import TransportMessage
from services import Services


class Client:

    def __init__(self, serverId) -> None:
        asyncio.run(self._intializeConnection(serverId))

    async def _intializeConnection(self,serverId):
        self.socket = socketio.AsyncClient()
        await self.socket.connect(serverId)
        await self.socket.wait()

    def subscribe(self, topics):
        if not isinstance(topics, list):
            topics = [topics]

        for t in topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=t)
            self.socket.emit("SUBSCRIBE_TOPIC", json.dump(tMessage))

    def unsubscribe(self, topics):
        if not isinstance(topics, list):
            topics = [topics]

        for t in topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=t)
            self.socket.emit("UNSUBSCRIBE_TOPIC", json.dump(tMessage))

    def publish(self, topic, message):
        pass

    def listTopics(self):
        tMessage = TransportMessage(timestamp=time.time())
        self.socket.emit("LIST_TOPICS", json.dump(tMessage))

    def getTopicStatus(self, topic):
        pass

    def handleUpdateTopic(message):
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Client",
        description="Client for Publisher"
    )

    parser.add_argument("-sub", "--subscribe", nargs="+", help="list of topics to subscribe", metavar="TOPIC")
    parser.add_argument("-p", "--publish", help="published topic", metavar="TOPIC")
    parser.add_argument("-m", "--message", help="message to be published to topic", metavar="STRING")
    parser.add_argument("-l", "--list", action="store_true", help="get all list topics from server")
    parser.add_argument("-s", "--server", required=True, help="server address", metavar="ADDRESS:PORT")

    args = parser.parse_args()

    # call client functions
    cli = Client(args.server)

    if args.sub:
        try:
            cli.subscribe(args.subscribe)
        except KeyboardInterrupt: # Catch Ctrl+C TODO: use exit handler
            cli.unsubscribe(args.subscribe)
            sys.exit()

    elif args.publish and args.message:
        cli.publish(args.publish, args.subscribe)

    elif args.list:
        cli.listTopics(args.list)

    else:
        print("No action, please check your parameters")
    
    sys.exit()

