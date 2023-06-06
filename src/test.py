import socketio
import time
import pytest
from client import Client
from transport_message import TransportMessage

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
    client = socketio.Client(logger=False)
    client.connect("http://localhost:8080")
    client.on("*", answers2)
    yield client
    client.disconnect()


@pytest.fixture
def user_client():
    client = Client("http://localhost:8080")
    yield client
    client.disconnect()


@pytest.fixture
def user_client2():
    client = Client("http://localhost:8080")
    yield client
    client.disconnect()


def test_subscribe(client, client2):
    global RESPOSE1
    global RESPOSE2
    RESPOSE1 = None
    RESPOSE2 = None
    sub_topic = "test"
    emit_topic = "SUBSCRIBE_TOPIC"

    # TODO: Check topic is None

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


def test_subscribe_client(capsys, user_client):
    sub_topic = "test_topic"

    user_client.subscribe(sub_topic)
    time.sleep(0.5)

    expected_str = f"======= SUBSCRIBED TO {sub_topic} ======="
    output_list = capsys.readouterr()[0].split("\n")

    assert output_list[0] == expected_str


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

    RESPOSE1 = None
    RESPOSE2 = None

    # Publish second message to topic
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

    RESPOSE1 = None
    RESPOSE2 = None


def test_publish_client(capsys, user_client, user_client2):
    sub_topic = "test_topic"
    not_sub_topic = "i do not exist"
    msg_publish = "this is a message"

    with capsys.disabled():
        user_client2.subscribe(sub_topic)
        time.sleep(0.5)

    # Publish to a topic
    user_client.publish(sub_topic, msg_publish)
    time.sleep(0.5)

    expected_msg1 = f"Message: {msg_publish}"
    expected_msg2 = f"Successfully published message to {sub_topic}."
    output_list = capsys.readouterr()[0].split("\n")

    assert output_list[1] == expected_msg1
    # from user_client2 "test_topic (06-06-2023 10:21:16): this is a message""
    assert output_list[3] == expected_msg2

    # Publish to a topic that does not exist
    user_client2.publish(not_sub_topic, msg_publish)
    time.sleep(0.5)

    expected_msg = f"{not_sub_topic} does not exist."
    output_list2 = capsys.readouterr()[0].split("\n")

    assert output_list2[2] == expected_msg


def test_unsubscribe(client, client2):
    global RESPOSE1
    global RESPOSE2
    RESPOSE1 = None
    RESPOSE2 = None
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

    # Unsubscribe from topic that is already unsubscribed
    client2.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    assert client2.connected
    assert RESPOSE2[0] == "PRINT_MESSAGE_AND_EXIT"

    data = TransportMessage.parse_raw(RESPOSE2[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Not subscribed to {sub_topic}."

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


def test_unsubscribe_client():
    pass


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
    client.emit("SUBSCRIBE_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
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


def test_list_topics_client():
    pass


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
    assert isinstance(data.payload, str)  # only check if it is a string

    RESPOSE1 = None


def test_get_topic_status_client():
    pass


def test_heartbeat(client, client2):
    global RESPOSE1
    RESPOSE1 = None
    sub_topic = "test"
    emit_topic = "SUBSCRIBE_TOPIC"

    # Create new topic and subscribe
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # publish first message
    client2.emit("PUBLISH_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic, payload="12345").json())
    time.sleep(0.5)

    assert RESPOSE1 is not None
    RESPOSE1 = None

    # Wait 10 seconds
    time.sleep(10)

    # No message should be received
    assert RESPOSE1 is None

    # Wait 15 seconds. In sum 25 seconds (heartbeat interval is 20 seconds)
    time.sleep(15)

    # Check if the message is published
    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert sub_topic in data.payload
    assert "12345" in data.payload


def test_cleanup_topic(client):
    global RESPOSE1
    RESPOSE1 = None
    sub_topic = "test"
    emit_topic = "SUBSCRIBE_TOPIC"

    # Create new topic and subscribe
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # publish first message
    client.emit("PUBLISH_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic, payload="12345").json())
    time.sleep(0.5)

    assert RESPOSE1 is not None
    RESPOSE1 = None

    # Unsubscribe from topic
    client.emit("UNSUBSCRIBE_TOPIC", TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    # Subscribe again and check if the topic is created again
    client.emit(emit_topic, TransportMessage(timestamp=int(time.time()), topic=sub_topic).json())
    time.sleep(0.5)

    assert client.connected
    assert RESPOSE1[0] == "PRINT_MESSAGE"

    data = TransportMessage.parse_raw(RESPOSE1[1])
    assert data.timestamp is not None
    assert data.topic is None
    assert data.payload == f"Created {sub_topic} and successfully subscribed."
