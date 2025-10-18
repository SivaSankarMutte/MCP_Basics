# client.py
import requests
from typing import Optional, Dict, Any

class MCPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    # 1️⃣ Create a new context
    def create_context(self, metadata: Dict = None, conversation: list = None):
        payload = {
            "metadata": metadata or {},
            "payload": {
                "conversation": conversation or []
            }
        }
        r = requests.post(f"{self.base_url}/contexts", json=payload)
        r.raise_for_status()
        return r.json()

    # 2️⃣ Get a context by ID
    def get_context(self, context_id: str):
        r = requests.get(f"{self.base_url}/contexts/{context_id}")
        r.raise_for_status()
        return r.json()

    # 3️⃣ Patch a context
    def patch_context(self, context_id: str, patch_ops: list):
        r = requests.patch(f"{self.base_url}/contexts/{context_id}", json=patch_ops)
        r.raise_for_status()
        return r.json()

    # 4️⃣ Infer — send a prompt and get response
    def infer(self, prompt: str, context_id: Optional[str] = None, context: Optional[Dict] = None):
        payload = {
            "prompt": prompt
        }
        if context_id:
            payload["context_id"] = context_id
        elif context:
            payload["context"] = context

        r = requests.post(f"{self.base_url}/infer", json=payload)
        
        r.raise_for_status()
        return r.json()
