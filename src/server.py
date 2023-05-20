"""Server for publisher subscriber system. For more information, please run `python server.py --help`"""

import asyncio
import time
import logging
from argparse import ArgumentParser
from datetime import datetime
from threading import Thread
from typing import List, Optional

import socketio
from aiohttp import web

from transport_message import TransportMessage

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ParallelTimer(Thread):
    def __init__(self, server) -> None:
        super().__init__()
        self.server = server

    def run(self):
        while 1:
            heartbeat = self.server.heart_beat(20)
            asyncio.run(heartbeat)


class Topic:
    """Class to manage the Topics with needed data."""

    name = None
    """name of the topic"""
    content = None
    """content of the topic"""
    subscribers: List[str] = []
    """list of subscribers"""
    timestamp = None
    """timestamp"""
    last_update = None
    """last update of topic"""


class Server:
    def __init__(self) -> None:
        self.list_of_topics: List[Topic] = []

        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.sio.event(self.connect)
        self.sio.on("SUBSCRIBE_TOPIC", self.handle_subscribe)
        self.sio.on("UNSUBSCRIBE_TOPIC", self.handle_unsubscribe)
        self.sio.on("PUBLISH_TOPIC", self.handle_publish)
        self.sio.on("LIST_TOPICS", self.handle_list_topics)
        self.sio.on("GET_TOPIC_STATUS", self.handle_topic_status)

    @staticmethod
    def _check_data_none_decorator(func):
        """Decorator for checking if data is None.
        If data is None, the client will receive an error message.
        """

        async def wrapper(self, sid, data=None):
            if data is None:
                response = TransportMessage(
                    timestamp=int(time.time()), payload="Missing payload of type TransportMessage."
                )
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                logging.error(response.payload)
                return None
            return await func(self, sid, data)

        return wrapper

    @staticmethod
    def _check_topic_decorator(func):
        """Decorator for checking if topic exists.
        If topic does not exist, the client will receive an error message.
        """

        async def wrapper(self, sid, data):
            try:
                parsed_data = TransportMessage.parse_raw(data)
            except Exception:
                response = TransportMessage(timestamp=int(time.time()), payload="Invalid payload.")
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                logging.error(response.payload)
                return None

            # Check if data contains topic
            if parsed_data.topic is None:
                response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                logging.error(response.payload)
                return None
            return await func(self, sid, data)

        return wrapper

    async def connect(self, sid, environ, auth=None):
        """Called when a client connects to the server.

        :param sid: Generated session id
        :param environ: Environment variables
        :param auth: Unused
        """
        logging.info("SID: %s connected (%s)", sid, environ["REMOTE_ADDR"])

    @_check_data_none_decorator
    @_check_topic_decorator
    async def handle_subscribe(self, sid, data=None) -> None:
        """Called when a client subscribes to a topic.
        If the topic does not exist, it will be created. If the client is already subscribed to the topic, nothing
        happens. Otherwise the client will be subscribed to the topic and will receive updates.

        :param sid: Generated session id
        :param data: Data sent by the client
        """

        data = TransportMessage.parse_raw(data)
        topic = self._get_topic_by_name(data.topic)
        if topic is not None:
            # Check if sid already subscribed to topic
            if sid in topic.subscribers:
                response = TransportMessage(timestamp=int(time.time()), payload=f"Already subscribed to {data.topic}.")
            else:
                # Subscribe to topic
                topic.subscribers.append(sid)
                response = TransportMessage(
                    timestamp=int(time.time()), payload=f"Successfully subscribed to {data.topic}."
                )
        else:
            # Create new topic if not already existing and subscribe
            new_topic = Topic()
            new_topic.name = data.topic
            new_topic.subscribers.append(sid)
            self.list_of_topics.append(new_topic)
            response = TransportMessage(
                timestamp=int(time.time()), payload=f"Created {data.topic} and successfully subscribed."
            )

        await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)
        logging.info(response.payload)

    @_check_data_none_decorator
    @_check_topic_decorator
    async def handle_unsubscribe(self, sid, data=None) -> None:
        """Called when a client unsubscribes from a topic.
        The client will be unsubscribed from the topic and will not receive any updates.

        :param sid: Generated session id
        :param data: Data sent by the client
        """

        data = TransportMessage.parse_raw(data)
        topic = self._get_topic_by_name(data.topic)

        if topic is not None:
            # Check if sid subscribed to topic and unsubscribe
            if sid in topic.subscribers:
                topic.subscribers.remove(sid)
                response = TransportMessage(
                    timestamp=int(time.time()), payload=f"Successfully unsubscribed from {data.topic}."
                )
            else:
                # Not subscribed
                response = TransportMessage(timestamp=int(time.time()), payload=f"Not subscribed to {data.topic}.")

        else:
            # Topic not existing
            response = TransportMessage(timestamp=int(time.time()), payload=f"{data.topic} does not exist.")

        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
        logging.info(response.payload)

    @_check_data_none_decorator
    @_check_topic_decorator
    async def handle_publish(self, sid, data=None) -> None:
        """Called when a client publishes a message to a topic.
        The message will be published to the topic and all subscribers will receive the message.

        :param sid: Generated session id
        :param data: Data sent by the client
        """
        data = TransportMessage.parse_raw(data)
        topic = self._get_topic_by_name(data.topic)

        # Check if data contains payload
        if data.payload is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter message.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None

        if topic is not None:
            # Publish message to topic
            topic.content = data.payload
            topic.timestamp = data.timestamp
            response = TransportMessage(
                timestamp=int(time.time()), payload=f"Successfully published message to {data.topic}."
            )
            await self.update_topic(topic)
        else:
            # Topic not existing
            response = TransportMessage(timestamp=int(time.time()), payload=f"{data.topic} does not exist.")

        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
        logging.info(response.payload)

    async def handle_list_topics(self, sid, data=None) -> None:
        """Called when a client requests a list of all topics.
        The client will receive a list of all topics.

        :param sid: Generated session id
        :param data: Data sent by the client. Unused
        """
        response_msg = "All topics on the server:"
        for topic in self.list_of_topics:
            response_msg += f"\n{topic.name}"

        response = TransportMessage(timestamp=int(time.time()), payload=response_msg)
        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
        logging.info(response.payload)

    @_check_data_none_decorator
    @_check_topic_decorator
    async def handle_topic_status(self, sid, data=None) -> None:
        """Called when a client requests the status of a topic.
        The client will receive the status of the topic.

        :param sid: Generated session id
        :param data: Data sent by the client
        """

        data = TransportMessage.parse_raw(data)
        topic = self._get_topic_by_name(data.topic)

        if topic is not None:
            subscribers = ""
            for subscriber in topic.subscribers:
                subscribers.join(f"\t{subscriber}\n\t")
            if topic.content is None or topic.timestamp is None:
                topic_status = f"\ntopic name:\t{topic.name}\n\nsubscribers:{subscribers}\n\nThere was no publish on this topic yet."
            else:
                topic_status = f"\ntopic name:\t{topic.name}\n\ntimestamp:\t{datetime.fromtimestamp(int(topic.timestamp)).strftime('%d-%m-%Y %H:%M:%S')}\n\ncontent:\t{topic.content}\n\nsubscribers:{subscribers}"
            response = TransportMessage(timestamp=int(time.time()), payload=topic_status)
        else:
            # Topic not existing
            response = TransportMessage(timestamp=int(time.time()), payload=f"{data.topic} does not exist.")

        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
        logging.info(response.payload)

    async def update_topic(self, topic: Topic) -> None:
        """Called when a topic is updated.
        The subscribers of the topic will receive the updated topic.

        :param topic: The topic
        """
        topic.last_update = int(time.time())
        response = TransportMessage(
            timestamp=int(time.time()),
            payload=f"{topic.name} ({datetime.fromtimestamp(int(topic.timestamp)).strftime('%d-%m-%Y %H:%M:%S')}): {topic.content}",
        )
        for sub in topic.subscribers:
            await self.sio.emit("PRINT_MESSAGE", response.json(), room=sub)
            logging.info("Publish to %s: %s", topic.name, response.payload)

    async def heart_beat(self, time_delta):
        """Go through all topics and check if they were updated in the last time_delta seconds.
        If not, update the topic.

        :param time_delta: Time in seconds
        """
        for topic in self.list_of_topics:
            if topic.last_update is not None and int(time.time()) - topic.last_update > time_delta:
                await self.update_topic(topic)
                logging.info("Topic %s was updated through heart beat.", topic.name)

    def _get_topic_by_name(self, name: str) -> Optional[Topic]:
        """Get a topic by its name.

        :param name: Name of the topic
        :return: Topic object
        """
        for topic in self.list_of_topics:
            if topic.name == name:
                return topic
        return None


def get_app():
    """Create an ASGI application for the server.

    :return: ASGI application
    """
    server = Server()
    application = web.Application()
    server.sio.attach(application)

    timer = ParallelTimer(server)
    timer.start()

    return application


if __name__ == "__main__":
    parser = ArgumentParser(prog="server.py", description="Starts a server for publisher subscriber system")
    parser.add_argument(
        "-p", "--port", type=str, help="Port to run the server on. Default is 8080", default=8080, metavar="PORT"
    )
    parser.add_argument(
        "--host", type=str, help="Host to run the server on. Default is localhost", default="127.0.0.1", metavar="HOST"
    )
    params = parser.parse_args()

    # wrap with ASGI application
    app = get_app()
    web.run_app(app, host=params.host, port=params.port)
