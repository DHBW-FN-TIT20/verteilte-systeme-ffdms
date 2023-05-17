import atexit
import socketio
import argparse
import time
import json
import sys

from transport_message import TransportMessage

class Client:

    def __init__(self, server_id) -> None:
        self.socket = socketio.Client()
        self.socket.connect(server_id)

        self.socket.on("PRINT_MESSAGE", self._handleResponse)
        self.socket.on("PRINT_MESSAGE_AND_EXIT", self._handleExitResponse)

        self.subscribed_topics = []

    def subscribe(self, topics):

        self.subscribed_topics = topics
        # string to list
        if not isinstance(topics, list):
            self.subscribed_topics = [topics]

        print(f"======= SUBSCRIBED TO {', '.join(self.subscribed_topics)} =======\n")
        for topic in self.subscribed_topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=topic)
            self.socket.emit("SUBSCRIBE_TOPIC", tMessage.json())

    def unsubscibe(self):

        print("exxxiiittt")

        # Unsubscribe        
        # print(f"======= UNSUBSCRIBED FROM {', '.join(self.subscribed_topics)} =======")
        #for topic in self.subscribed_topics:
        #    tMessage = TransportMessage(timestamp=time.time(), topic=topic)
        #    self.socket.emit("UNSUBSCRIBE_TOPIC", tMessage.json())
        
        # Disconnect
        self.socket.disconnect()

    def publish(self, topic, message):
        print(f"======= PUBLISH MESSAGE =======")
        print(f"Message: {message}")
        tMessage = TransportMessage(timestamp=time.time(), topic=topic, payload=message)
        self.socket.emit("PUBLISH_TOPIC", tMessage.json())

    def listTopics(self):
        tMessage = TransportMessage(timestamp=time.time())
        self.socket.emit("LIST_TOPICS", tMessage.json())

    def getTopicStatus(self, topic):
        tMessage = TransportMessage(timestamp=time.time(), topic=topic)
        self.socket.emit("GET_TOPIC_STATUS", tMessage.json())
    
    def _handleResponse(self, response):
        response_dict = json.loads(response)
        print(f"{response_dict['payload']}")
    
    def _handleExitResponse(self, response):
        self._handleResponse(response)
        
        # Exit
        self.socket.disconnect()
        sys.exit(0)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Client",
        description="Client for Publisher"
    )

    parser.add_argument("-sub", "--subscribe", nargs="+", help="list of topics to subscribe", metavar="TOPIC")
    parser.add_argument("-p", "--publish", help="published topic", metavar="TOPIC")
    parser.add_argument("-m", "--message", help="message to be published to topic", metavar="STRING")
    parser.add_argument("-l", "--list", action="store_true", help="get all list topics from server")
    parser.add_argument("-st", "--status", help="get topic status from server")
    parser.add_argument("-s", "--server", required=True, help="server address", metavar="ADDRESS:PORT")

    args = parser.parse_args()

    # call client functions
    cli = Client(args.server)

    if args.subscribe:
        cli.subscribe(args.subscribe)
        atexit.register(cli.unsubscibe)

    elif args.publish and args.message:
        cli.publish(args.publish, args.message)

    elif args.list:
        cli.listTopics()
    
    elif args.status:
        cli.getTopicStatus(args.status)

    else:
        print("No action, please check your parameters")
    

