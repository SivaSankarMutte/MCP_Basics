### Model Context Protocol (MCP) Chat Application
This project is a fully functional Model Context Protocol (MCP) prototype built using Python, FastAPI, and Groq LLM. It supports:
  Dynamic context creation
  Versioned conversation storage
  Real-time streaming of assistant responses via WebSockets
  A web-based chat UI
  Environment variable management for API keys

# Features
  Dynamic Context Management
    Each chat session gets a unique context ID.
    Context stores the full conversation (user + assistant messages).
    Context can be persisted in memory (for testing) or Redis (for production).
  Groq LLM Integration
    Uses the Groq API to generate assistant responses.
    Supports streaming simulation token-by-token to the client.
  WebSocket Streaming
    Persistent WebSocket connection for multiple messages per session.
    Streams tokens in real-time to the web UI.
  Web Chat Interface
    Single-page HTML + JavaScript UI.
    Supports sending messages, streaming responses, and starting new chats.
    Dynamic context creation per session.
    Conversation history loads automatically when reconnecting to a context.
  Environment Variables
    API keys (e.g., Groq API key) loaded from .env using python-dotenv.
    Keeps secrets out of the source code.
