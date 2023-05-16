from enum import Enum

class Services(Enum):
    SUBSCRIBE_TOPIC = 0
    UNSUBSCRIBE_TOPIC = 1
    PUBLISH_TOPIC=2
    LIST_TOPICS=3
    UPDATE_TOPIC=4
