from mcp.server.fastmcp import FastMCP
from rag_engine import RAGEngine
import json
import re
import os
import secrets
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── API Key Setup ────────────────────────────────────────────────────────────
# On first run, a key is auto-generated and saved to .env
# You can also set MCP_API_KEY manually in your environment

API_KEY_FILE = ".api_key"

def load_or_generate_api_key() -> str:
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            key = f.read().strip()
            if key:
                return key
    # Generate a new key
    key = secrets.token_urlsafe(32)
    with open(API_KEY_FILE, "w") as f:
        f.write(key)
    return key

API_KEY = os.getenv("MCP_API_KEY")
if not API_KEY:
    API_KEY = load_or_generate_api_key()

# ─── MCP Server ───────────────────────────────────────────────────────────────

mcp = FastMCP("Samvidhan AI")

# ─── RAG Engine ───────────────────────────────────────────────────────────────

try:
    rag_engine = RAGEngine()
    print("RAGEngine initialized successfully for MCP server.")
except Exception as e:
    print(f"Failed to initialize RAGEngine: {e}")
    rag_engine = None

# ─── Helper ───────────────────────────────────────────────────────────────────

def process_legal_query(query: str, language: str = "en") -> str:
    """Core logic shared by MCP tool and REST API."""
    if not rag_engine:
        return "Error: RAGEngine is not initialized."

    try:
        results = rag_engine.query(query)
        documents = results['documents'][0]

        response_text, external_citations = rag_engine.generate_response(query, documents, language)

        clean_json = re.sub(r"```json\n|```", "", response_text).strip()
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            return f"Raw Response (JSON parse failed): {response_text}"

        output = f"**Domain:** {data.get('domain', 'General')}\n\n"
        output += f"**Relevant Laws:** {', '.join(data.get('relevant_laws', []))}\n\n"
        output += f"**Explanation:**\n{data.get('explanation', '')}\n\n"
        output += f"**General Guidance:**\n{data.get('general_guidance', '')}\n\n"

        if data.get('confidence'):
            output += f"**Confidence:** {data.get('confidence')}\n\n"

        output += f"**Disclaimer:** {data.get('disclaimer', '')}\n\n"

        if external_citations:
            output += "**External Citations:**\n"
            for ext in external_citations:
                output += f"- {ext.get('summary')} ({ext.get('url')})\n"

        return output

    except Exception as e:
        return f"Error processing query: {str(e)}"

# ─── MCP Tool (for Claude / MCP clients) ─────────────────────────────────────

@mcp.tool()
def query_legal_assistant(query: str, language: str = "en") -> str:
    """
    Ask a legal question to the Samvidhan AI assistant.

    Args:
        query: The legal question or query to ask.
        language: The language for the response (default: "en").

    Returns:
        A formatted string containing legal advice, relevant laws, and explanation.
    """
    return process_legal_query(query, language)

# ─── FastAPI HTTP Server (for your website) ───────────────────────────────────

api = FastAPI(
    title="Samvidhan AI API",
    description="Legal Assistant API powered by Samvidhan AI MCP Server",
    version="1.0.0",
)

# Allow requests from your website (update origins as needed)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace "*" with your website URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class QueryRequest(BaseModel):
    query: str
    language: str = "en"

# Auth dependency
def verify_api_key(x_api_key: str = Header(..., description="Your API key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return x_api_key

# ── Endpoints ──────────────────────────────────────────────────────────────────

@api.get("/", tags=["Info"])
def root():
    return {
        "service": "Samvidhan AI",
        "status": "running",
        "docs": "/docs",
    }

@api.get("/setup", tags=["Setup"])
def setup():
    """
    Call this once to get your API key.
    Save the key and use it as the X-API-Key header in all requests.
    """
    return {
        "api_key": API_KEY,
        "usage": {
            "header": "X-API-Key",
            "example_curl": (
                f'curl -X POST http://localhost:8000/query '
                f'-H "X-API-Key: {API_KEY}" '
                f'-H "Content-Type: application/json" '
                f'-d \'{{"query": "What are my tenant rights?"}}\''
            ),
        },
        "note": "This key is saved in .api_key file. Set MCP_API_KEY env var to override.",
    }

@api.post("/query", tags=["Legal Assistant"])
def query_endpoint(body: QueryRequest, api_key: str = Header(None, alias="X-API-Key")):
    """
    Send a legal query and get a response from Samvidhan AI.
    Requires X-API-Key header.
    """
    verify_api_key(api_key)
    result = process_legal_query(body.query, body.language)
    return {
        "query": body.query,
        "language": body.language,
        "response": result,
    }

@api.get("/health", tags=["Info"])
def health():
    return {
        "status": "healthy",
        "rag_engine": "ready" if rag_engine else "not initialized",
        "api_key_configured": True,
    }

# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Samvidhan AI MCP + API Server")
    print("="*50)
    print(f"\n  API Key : {API_KEY}")
    print(f"  Setup   : http://localhost:8001/setup")
    print(f"  Docs    : http://localhost:8001/docs")
    print(f"  Query   : POST http://localhost:8001/query")
    print("="*50 + "\n")

    uvicorn.run(api, host="0.0.0.0", port=8001)