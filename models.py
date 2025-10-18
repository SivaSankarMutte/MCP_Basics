# models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import uuid4

class Message(BaseModel):
    role: str
    text: str

class Payload(BaseModel):
    conversation: List[Message] = []

class Context(BaseModel):
    context_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: Dict[str, str] = {}
    payload: Payload = Field(default_factory=Payload)

# models.py (add at bottom)
class ContextPatch(BaseModel):
    expected_version: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None
    payload: Optional[Payload] = None


class InferenceRequest(BaseModel):
    context_id: Optional[str] = None   # existing context id
    context: Optional[Context] = None  # or directly send context
    prompt: str                        # user question / message
    options: Optional[Dict[str, Any]] = None
