import socketio
import json
import time
from aiohttp import web
from argparse import ArgumentParser
from typing import List
from transport_message import TransportMessage


parser = ArgumentParser(prog="server.py", description="Starts a server for publisher subscriber system")
parser.add_argument(
    "-p", "--port", type=str, help="Port to run the server on. Default is 8080", default=8080, metavar="PORT"
)
parser.add_argument(
    "--host", type=str, help="Host to run the server on. Default is localhost", default="127.0.0.1", metavar="HOST"
)


class Topic:
    def __init__(self) -> None:
        self.name = None
        self.content = None
        self.subscribers: List[str] = []
        self.timestamp = None


sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")

list_of_topics: List[Topic] = []


@sio.event
def connect(sid, environ, auth):
    print("connect ", sid)


@sio.on("SUBSCRIBE_TOPIC")
async def handle_subscribe(sid, data) -> None:
    data = json.loads(data)
    # Check if data contains topic
    if data["topic"] is None:
        response = TransportMessage(timestamp=int(time.time()), payload="Missing parameter topic.")
        await sio.emit("UNSUBSCRIBE_TOPIC", response.json(), room=sid)
        return None
    # Check if topic already exists
    for topic in list_of_topics:
        if topic.name == data["topic"]:
            # Check if sid already subscribed to topic
            if sid in topic.subscribers:
                response = TransportMessage(timestamp=int(time.time()), payload=f"Already subscribed to {data['topic']}.")
                await sio.emit("SUBSCRIBE_TOPIC", response.json(), room=sid)
                return None
            # Subscribe to topic
            topic.subscribers.append(sid)
            response = TransportMessage(timestamp=int(time.time()), payload=f"Successfully subscribed to {data['topic']}.")
            await sio.emit("SUBSCRIBE_TOPIC", response.json(), room=sid)
            return None
    # Create new topic if not already existing and subscribe
    new_topic = Topic()
    new_topic.name = data["topic"]
    new_topic.subscribers.append(sid)
    list_of_topics.append(new_topic)
    response = TransportMessage(timestamp=int(time.time()), payload=f"Created {data['topic']} and successfully subscribed.")
    await sio.emit("SUBSCRIBE_TOPIC", response.json(), room=sid)


@sio.on("UNSUBSCRIBE_TOPIC")
async def handle_unsubscribe(self, sid, data) -> None:
    pass


@sio.on("PUBLISH_TOPIC")
async def handle_publish(self) -> None:
    pass


@sio.on("LIST_TOPICS")
async def handle_list_topics(self) -> None:
    pass


@sio.on("GET_TOPIC_STATUS")
async def handle_topic_status(self) -> None:
    pass


def update_topic(self) -> None:
    pass


if __name__ == "__main__":
    args = parser.parse_args()

    # wrap with ASGI application
    app = web.Application()
    sio.attach(app)

    web.run_app(app, host=args.host, port=args.port)
