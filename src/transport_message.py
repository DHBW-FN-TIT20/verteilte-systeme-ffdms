from pydantic import BaseModel
from typing import Optional


class TransportMessage(BaseModel):
    """Base class for transport messages"""
    timestamp: int
    """Timestamp of message"""

    topic: Optional[str]
    """Topic of message"""
    
    payload: Optional[str]
    """Payload of message"""
