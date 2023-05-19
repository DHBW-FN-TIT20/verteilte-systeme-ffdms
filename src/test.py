import socketio
from transport_message import TransportMessage
import time
import json
import pytest

RESPOSE1 = None
RESPOSE2 = None

def answers1(*data):
    global RESPOSE1
    RESPOSE1 = data

def answers2(*data):
    global RESPOSE2
    RESPOSE2 = data

@pytest.fixture
def client():
    client = socketio.Client()
    client.connect("http://localhost:8080")
    client.on("*", answers1)
    yield client
    client.disconnect()

@pytest.fixture
def client2():
    client = socketio.Client()
    client.connect("http://localhost:8080")
    client.on("*", answers2)
    yield client
    client.disconnect()


def test_subscribe(client, client2):
    global RESPOSE1
    global RESPOSE2
    RESPOSE1 = None
    RESPOSE2 = None
    sub_topic = "test"
    emit_topic = "SUBSCRIBE_TOPIC"

    #TODO: Check topic is None

    # Subscribe to new topic wihout payload
    client.emit(emit_topic)
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"
    
    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == "Missing payload of type TransportMessage."
    
    RESPOSE1 = None

    # Subscribe to new topic without topic
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time())).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == "Missing parameter topic."

    RESPOSE1 = None

    # Subscribe to new topic
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)
 
    # Check message for the first client
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE"
    
    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Created {sub_topic} and successfully subscribed."

    RESPOSE1 = None

    # Check message for the second client
    assert client2.connected
    assert RESPOSE2 is None

    # Subscribe to the same topic
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Already subscribed to {sub_topic}."

    RESPOSE1 = None

    # Check message for the second client
    assert client2.connected
    assert RESPOSE2 is None

    # Subscribe to a new topic that already exists
    client2.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)
    assert client2.connected
    assert RESPOSE2[0] == "PRINT_MESSAGE"

    data = TransportMessage.parse_raw(RESPOSE2[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Successfully subscribed to {sub_topic}."

    RESPOSE2 = None

    # Check message for the first client
    assert client.connected
    assert RESPOSE1 is None


def test_publish(client, client2):
    global RESPOSE1
    global RESPOSE2
    RESPOSE1 = None
    RESPOSE2 = None
    sub_topic = "test"
    emit_topic = "PUBLISH_TOPIC"
    payload = "test payload"

    # Publish to topic that does not exist
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic, payload=payload).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"{sub_topic} does not exist."

    RESPOSE1 = None

    # Create new topic and subscribe
    client.emit("SUBSCRIBE_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Publish to topic
    client2.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic, payload=payload).json())
    time.sleep(0.5)

    # Check if publisher is notified
    assert client2.connected
    assert RESPOSE2[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE2[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Successfully published message to {sub_topic}."

    # Check if the message is published
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload.split(": ")[1] == payload


def test_unsubscribe(client):
    global RESPOSE1
    RESPOSE1 = None
    sub_topic = "test"
    emit_topic = "UNSUBSCRIBE_TOPIC"

    # Unsubscribe from topic that does not exist
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"{sub_topic} does not exist."

    RESPOSE1 = None

    # Create new topic and subscribe
    client.emit("SUBSCRIBE_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Unsubscribe from topic
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Check if the message is published
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Successfully unsubscribed from {sub_topic}."

    RESPOSE1 = None

    # Unsubscribe from topic that is already unsubscribed
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Not subscribed to {sub_topic}."

    #TODO: Check if the topic is deleted


def test_list_topics(client):
    global RESPOSE1
    RESPOSE1 = None
    sub_topic = "test"
    emit_topic = "LIST_TOPICS"

    # List topics when there are no topics
    client.emit(emit_topic)
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == "All topics on the server:"

    RESPOSE1 = None

    # Create new topic and subscribe
    client.emit("SUBSCRIBE_TOPIC")
    time.sleep(0.5)

    # List topics
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time())).json())
    time.sleep(0.5)

    # Check if the message is published
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"All topics on the server:\n{sub_topic}"

    RESPOSE1 = None

def test_get_topic_status(client):
    global RESPOSE1
    RESPOSE1 = None
    sub_topic = "test"
    emit_topic = "GET_TOPIC_STATUS"

    # Get status of topic that does not exist
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"{sub_topic} does not exist."

    RESPOSE1 = None

    # Create new topic and subscribe
    client.emit("SUBSCRIBE_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Get status of topic
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Check if the message is published
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert isinstance(data.payload, str)    # only check if it is a string 

    RESPOSE1 = None
