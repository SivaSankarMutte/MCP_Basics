# test_client.py
from client import MCPClient

client = MCPClient("http://127.0.0.1:8000")

# 1. Create a new context
ctx = client.create_context(
    metadata={"user": "Siva"},
    conversation=[{"role": "user", "text": "Hello MCP!"}]
)
print("Created context:", ctx)

context_id = ctx["context_id"]

# 2. Infer something
res = client.infer(prompt="What is the meaning of life?", context_id=context_id)
print("Inference result:", res)

# 3. Fetch updated context
updated = client.get_context(context_id)
print("Updated context:", updated)
