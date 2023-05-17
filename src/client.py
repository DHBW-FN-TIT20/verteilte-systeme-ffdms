import atexit
import socketio
import argparse
import time
import json
import sys, os
from contextlib import redirect_stderr
from transport_message import TransportMessage

class Client:
    """
    Client object for publisher server
    """

    def __init__(self, server_id) -> None:
        """Constructor, init socket and variables

        :param server_id: server address
        :type server_id: string
        """
        self.socket = socketio.Client()
        try:
            self.socket.connect(server_id)
        except socketio.exceptions.ConnectionError:
            print(f"No connection to {server_id}, please make sure the server is available.")
            sys.exit(0)

        self.socket.on("PRINT_MESSAGE", self._handleResponse)
        self.socket.on("PRINT_MESSAGE_AND_EXIT", self._handleExitResponse)

        self.subscribed_topics = []

    def subscribe(self, topics) -> None:
        """
        Request to subscribe to topics, wait for server messages

        :param topics: topics
        :type topics: string or list of strings
        """

        self.subscribed_topics = topics
        # string to list
        if not isinstance(topics, list):
            self.subscribed_topics = [topics]

        print(f"======= SUBSCRIBED TO {', '.join(self.subscribed_topics)} =======\n")
        for topic in self.subscribed_topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=topic)
            self.socket.emit("SUBSCRIBE_TOPIC", tMessage.json())

    def unsubscibe(self) -> None:
        """
        Request to unsubscribe from topics in self.subscribed_topics and disconnect
        """

        print(f"\n======= UNSUBSCRIBED FROM {', '.join(self.subscribed_topics)} =======")
        for topic in self.subscribed_topics:
            tMessage = TransportMessage(timestamp=time.time(), topic=topic)
            self.socket.emit("UNSUBSCRIBE_TOPIC", tMessage.json())
        
        # Disconnect
        self.socket.disconnect()

    def publish(self, topic, message):
        """
        Request to publish a message to the topic

        :param topic: topic
        :type topic: string
        :param message: message for topic
        :type message: string
        """
        print(f"======= PUBLISH MESSAGE =======")
        print(f"Message: {message}")
        tMessage = TransportMessage(timestamp=time.time(), topic=topic, payload=message)
        self.socket.emit("PUBLISH_TOPIC", tMessage.json())

    def listTopics(self):
        """
        Request to list all topics avaliable
        """
        tMessage = TransportMessage(timestamp=time.time())
        self.socket.emit("LIST_TOPICS", tMessage.json())

    def getTopicStatus(self, topic):
        """
        Request to get topic status

        :param topic: topic
        :type topic: string
        """
        tMessage = TransportMessage(timestamp=time.time(), topic=topic)
        self.socket.emit("GET_TOPIC_STATUS", tMessage.json())
    
    def _handleResponse(self, response):
        """
        Receive PRINT_MESSAGE response from server

        :param response: response from server
        :type response: string
        """
        response_dict = json.loads(response)
        print(f"{response_dict['payload']}")
    
    def _handleExitResponse(self, response):
        """
        Receive PRINT_MESSAGE_AND_EXIT response from server

        :param response: response from server
        :type response: string
        """
        self._handleResponse(response)
        
        # Exit
        self.socket.disconnect()
        sys.exit(0)
        

if __name__ == "__main__":

    # workaround for
    # KeyboardInterrupt: "Exception ignored in: <module 'threading' from '/usr/lib/python3.10/threading.py'>"
    # To see error messages, comment those lines
    fnull = open(os.devnull, 'w')
    r = redirect_stderr(fnull)
    r.__enter__()

    # init parser
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
    
