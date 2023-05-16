import socketio
from transport_message import TransportMessage
import json
import time

from pydantic import BaseModel

# asyncio
sio = socketio.Client()

sio.connect("http://localhost:8080")

@sio.on('SUBSCRIBE_TOPIC')
def answer(data):
    print(data)

data = TransportMessage(timestamp=int(time.time()), topic="test", payload="test")
print(data.json())
sio.emit("SUBSCRIBE_TOPIC", data.json())

data = TransportMessage(timestamp=int(time.time()), topic="test", payload="test")
sio.emit("SUBSCRIBE_TOPIC", data.json())
