"""Server for publisher subscriber system. For more information, please run `python server.py --help`"""

import asyncio
import json
import time
from argparse import ArgumentParser
from datetime import datetime
from threading import Thread
from typing import List

import socketio
from aiohttp import web

from transport_message import TransportMessage

parser = ArgumentParser(prog="server.py", description="Starts a server for publisher subscriber system")
parser.add_argument(
    "-p", "--port", type=str, help="Port to run the server on. Default is 8080", default=8080, metavar="PORT"
)
parser.add_argument(
    "--host", type=str, help="Host to run the server on. Default is localhost", default="127.0.0.1", metavar="HOST"
)


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
    def __init__(self, args) -> None:
        self.list_of_topics: List[Topic] = []
        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.list_of_topics: List[Topic] = []
        self.sio.event(self.connect)
        self.sio.on("SUBSCRIBE_TOPIC", self.handle_subscribe)
        self.sio.on("UNSUBSCRIBE_TOPIC", self.handle_unsubscribe)
        self.sio.on("PUBLISH_TOPIC", self.handle_publish)
        self.sio.on("LIST_TOPICS", self.handle_list_topics)
        self.sio.on("GET_TOPIC_STATUS", self.handle_topic_status)

    async def connect(self, sid, environ, auth):
        print(f"{sid} connected ({environ['REMOTE_ADDR']})")

    async def handle_subscribe(self, sid, data=None) -> None:
        # Check if data is None
        if data is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Internal Server Error.")
            await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)
            return None
        data = json.loads(data)
        # Check if data contains topic
        if data["topic"] is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
            await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)
            return None
        # Check if topic already exists
        for topic in self.list_of_topics:
            if topic.name == data["topic"]:
                # Check if sid already subscribed to topic
                if sid in topic.subscribers:
                    response = TransportMessage(
                        timestamp=int(time.time()), payload=f"Already subscribed to {data['topic']}."
                    )
                    await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)
                    return None
                # Subscribe to topic
                topic.subscribers.append(sid)
                response = TransportMessage(
                    timestamp=int(time.time()), payload=f"Successfully subscribed to {data['topic']}."
                )
                await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)
                return None
        # Create new topic if not already existing and subscribe
        new_topic = Topic()
        new_topic.name = data["topic"]
        new_topic.subscribers.append(sid)
        self.list_of_topics.append(new_topic)
        response = TransportMessage(
            timestamp=int(time.time()), payload=f"Created {data['topic']} and successfully subscribed."
        )
        await self.sio.emit("PRINT_MESSAGE", response.json(), room=sid)

    async def handle_unsubscribe(self, sid, data=None) -> None:
        # Check if data is None
        if data is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Internal Server Error.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        data = json.loads(data)
        # Check if data contains topic
        if data["topic"] is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        # Check if topic exists
        for topic in self.list_of_topics:
            if topic.name == data["topic"]:
                # Check if sid subscribed to topic and unsubscribe
                if sid in topic.subscribers:
                    topic.subscribers.remove(sid)
                    response = TransportMessage(
                        timestamp=int(time.time()), payload=f"Successfully unsubscribed from {data['topic']}."
                    )
                    await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                    return None
                # Not subscribed
                response = TransportMessage(timestamp=int(time.time()), payload=f"Not subscribed to {data['topic']}.")
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                return None
        # Topic not existing
        response = TransportMessage(timestamp=int(time.time()), payload=f"{data['topic']} does not exist.")
        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)

    async def handle_publish(self, sid, data=None) -> None:
        # Check if data is None
        if data is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Internal Server Error.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        data = json.loads(data)
        # Check if data contains topic
        if data["topic"] is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        # Check if data contains payload
        if data["payload"] is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter message.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        # Check if topic exists
        for topic in self.list_of_topics:
            if topic.name == data["topic"]:
                topic.content = data["payload"]
                topic.timestamp = data["timestamp"]
                response = TransportMessage(
                    timestamp=int(time.time()), payload=f"Successfully published message to {data['topic']}."
                )
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                await self.update_topic(data["topic"])
                return None
        # Topic not existing
        response = TransportMessage(timestamp=int(time.time()), payload=f"{data['topic']} does not exist.")
        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)

    async def handle_list_topics(self, sid, data=None) -> None:
        response_msg = "All topics on the server:"
        for topic in self.list_of_topics:
            response_msg += f"\n{topic.name}"
        response = TransportMessage(timestamp=int(time.time()), payload=response_msg)
        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)

    async def handle_topic_status(self, sid, data=None) -> None:
        # Check if data is None
        if data is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Internal Server Error.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        data = json.loads(data)
        # Check if data contains topic
        if data["topic"] is None:
            response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
            await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
            return None
        # Check if topic exists
        for topic in self.list_of_topics:
            if topic.name == data["topic"]:
                subscribers = ""
                for s in topic.subscribers:
                    subscribers += f"\t{s}\n\t"
                if topic.content is None or topic.timestamp is None:
                    topic_status = f"\ntopic name:\t{topic.name}\n\nsubscribers:{subscribers}\n\nThere was no publish on this topic yet."
                else:
                    topic_status = f"\ntopic name:\t{topic.name}\n\ntimestamp:\t{datetime.fromtimestamp(int(topic.timestamp)).strftime('%d-%m-%Y %H:%M:%S')}\n\ncontent:\t{topic.content}\n\nsubscribers:{subscribers}"
                response = TransportMessage(timestamp=int(time.time()), payload=topic_status)
                await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)
                return None
        # Topic not existing
        response = TransportMessage(timestamp=int(time.time()), payload=f"{data['topic']} does not exist.")
        await self.sio.emit("PRINT_MESSAGE_AND_EXIT", response.json(), room=sid)

    async def update_topic(self, topic) -> None:
        for t in self.list_of_topics:
            if t.name == topic:
                t.last_update = int(time.time())
                response = TransportMessage(
                    timestamp=int(time.time()),
                    payload=f"{t.name} ({datetime.fromtimestamp(int(t.timestamp)).strftime('%d-%m-%Y %H:%M:%S')}): {t.content}",
                )
                # Top1 (17.05.2023, 09:12): Content hier
                for sub in t.subscribers:
                    await self.sio.emit("PRINT_MESSAGE", response.json(), room=sub)
                print("sent")

    async def heart_beat(self, time_delta):
        for topic in self.list_of_topics:
            if topic.last_update is not None and int(time.time()) - topic.last_update > time_delta:
                await self.update_topic(topic.name)
                print(f"updated {topic.name}")


if __name__ == "__main__":
    args = parser.parse_args()

    server = Server(args)

    timer = ParallelTimer(server)
    timer.start()

    # wrap with ASGI application
    app = web.Application()
    server.sio.attach(app)
    web.run_app(app, host=args.host, port=args.port)
