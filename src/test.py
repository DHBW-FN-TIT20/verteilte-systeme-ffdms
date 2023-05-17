import socketio
from transport_message import TransportMessage
import time
import json

# asyncio
sio = socketio.Client()

sio.connect("http://localhost:8080")

@sio.on('PRINT_MESSAGE')
def answer(data):
    data = json.loads(data)
    print(data["payload"])

@sio.on('PRINT_MESSAGE_AND_EXIT')
def answer(data):
    data = json.loads(data)
    print(data["payload"])

data = TransportMessage(timestamp=int(time.time()), topic="test", payload="test")
print(data.json())
sio.emit("SUBSCRIBE_TOPIC", data.json())

data = TransportMessage(timestamp=int(time.time()), topic="test", payload="test")
sio.emit("SUBSCRIBE_TOPIC", data.json())

data = TransportMessage(timestamp=int(time.time()), topic="test", payload="message")
sio.emit("PUBLISH_TOPIC", data.json())

data = TransportMessage(timestamp=int(time.time()), topic="test")
sio.emit("GET_TOPIC_STATUS", data.json())
