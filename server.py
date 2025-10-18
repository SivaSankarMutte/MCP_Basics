# server.py
from fastapi import FastAPI, HTTPException
from models import Context, ContextPatch
from storage import store
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="MCP Server")

# Allow your web UI origin (for testing we allow all)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/contexts")
def create_context(ctx: Context):
    store.save(ctx)
    return ctx

@app.get("/contexts/{context_id}")
def get_context(context_id: str):
    ctx = store.get(context_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Context not found")
    return ctx

@app.patch("/contexts/{context_id}")
def patch_context(context_id: str, patch: ContextPatch):
    ctx = store.get(context_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Context not found")

    # Check version
    if patch.expected_version is not None and patch.expected_version != ctx.version:
        raise HTTPException(status_code=409, detail="Version mismatch")

    # Apply updates
    if patch.metadata:
        ctx.metadata.update(patch.metadata)
    if patch.payload:
        ctx.payload = patch.payload

    ctx.version += 1
    ctx.updated_at = datetime.utcnow()

    store.save(ctx)
    return ctx



# Dummy AI generation (just reverse given string)
# from models import InferenceRequest, Message

# @app.post("/infer")
# def infer(req: InferenceRequest):
#     # Step 1: Get or use context
#     if req.context_id:
#         ctx = store.get(req.context_id)
#         if not ctx:
#             raise HTTPException(status_code=404, detail="Context not found")
#     elif req.context:
#         ctx = req.context
#     else:
#         raise HTTPException(status_code=400, detail="Need context_id or context")

#     # Step 2: Simulate a model reply
#     # We'll just reverse the prompt for now (a fake “AI” response)
#     fake_response = req.prompt[::-1]

#     # Step 3: Append to conversation
#     ctx.payload.conversation.append(Message(role="user", text=req.prompt))
#     ctx.payload.conversation.append(Message(role="assistant", text=fake_response))
#     ctx.version += 1

#     store.save(ctx)

#     # Step 4: Return updated conversation
#     return {
#         "context_id": ctx.context_id,
#         "version": ctx.version,
#         "response": fake_response,
#         "conversation": [m.dict() for m in ctx.payload.conversation]
#     }


# server.py
import os
from dotenv import load_dotenv
from models import InferenceRequest, Message
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Access the variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

@app.post("/infer")
def infer(req: InferenceRequest):
    # Step 1: Get or use context
    if req.context_id:
        ctx = store.get(req.context_id)
        if not ctx:
            raise HTTPException(status_code=404, detail="Context not found")
    elif req.context:
        ctx = req.context
    else:
        raise HTTPException(status_code=400, detail="Need context_id or context")

    # Step 2: Build full conversation
    messages = [{"role": m.role, "content": m.text} for m in ctx.payload.conversation]
    messages.append({"role": "user", "content": req.prompt})

    # Step 3: Call Groq LLM (Llama3 for example)
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {e}")

    # Step 4: Update conversation
    ctx.payload.conversation.append(Message(role="user", text=req.prompt))
    ctx.payload.conversation.append(Message(role="assistant", text=reply_text))
    ctx.version += 1
    store.save(ctx)

    # Step 5: Return updated info
    return {
        "context_id": ctx.context_id,
        "version": ctx.version,
        "response": reply_text,
        "conversation": [m.dict() for m in ctx.payload.conversation],
    }



from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from groq import Groq
from models import Message

# Already have: GROQ_API_KEY and groq_client

@app.websocket("/ws_infer/{context_id}")
async def ws_infer(websocket: WebSocket, context_id: str):
    await websocket.accept()

    # Get context
    ctx = store.get(context_id)
    if not ctx:
        await websocket.send_text("Context not found")
        await websocket.close()
        return

    try:
        while True:  # Keep connection alive for multiple messages
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            if not prompt:
                await websocket.send_text("No prompt provided")
                continue

            # Build conversation
            messages = [{"role": m.role, "content": m.text} for m in ctx.payload.conversation]
            messages.append({"role": "user", "content": prompt})

            # Call Groq
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
            )
            reply_text = response.choices[0].message.content

            # Stream token by token (simulate)
            for token in reply_text.split():
                await websocket.send_text(token + " ")
                await asyncio.sleep(0.02)

            # Update context
            ctx.payload.conversation.append(Message(role="user", text=prompt))
            ctx.payload.conversation.append(Message(role="assistant", text=reply_text))
            ctx.version += 1
            store.save(ctx)

            # Notify done
            await websocket.send_json({"event": "done", "version": ctx.version})

    except WebSocketDisconnect:
        print(f"Client disconnected: {context_id}")
    except Exception as e:
        await websocket.send_text(f"Error: {e}")
        await websocket.close()
