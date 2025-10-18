# storage.py
# in-memory (case-1)
# from typing import Dict
# from models import Context

# class InMemoryStore:
#     def __init__(self):
#         self.data: Dict[str, Context] = {}

#     def save(self, ctx: Context):
#         self.data[ctx.context_id] = ctx

#     def get(self, context_id: str):
#         return self.data.get(context_id)

# store = InMemoryStore()


# usage of redis
# storage.py
import redis
import json
from models import Context
from typing import Dict

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

class RedisStore:
    def __init__(self, redis_client):
        self.r = redis_client

    def save(self, ctx: Context):
        key = f"context:{ctx.context_id}"
        self.r.set(key, ctx.json())

    def get(self, context_id: str):
        key = f"context:{context_id}"
        data = self.r.get(key)
        if data:
            return Context.parse_raw(data)
        return None

store = RedisStore(r)
