from pydantic import BaseModel
from typing import Optional


class TransportMessage(BaseModel):
    timestamp: int
    topic: Optional[str]
    payload: Optional[str]
