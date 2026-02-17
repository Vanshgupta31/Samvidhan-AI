# Samvidhan AI - Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Google API Key (for Gemini)

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the `backend` directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Start the MCP Server
```bash
python mcp_server.py
```

The server will:
- Auto-generate an API key (saved in `.api_key`)
- Start on `http://localhost:8000`
- Display the API key in the console

### 4. Get Your API Key
Visit `http://localhost:8000/setup` to see:
- Your API key
- Example usage
- Integration instructions

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
Create a `.env.local` file in the `frontend` directory:
```env
NEXT_PUBLIC_MCP_API_KEY=your_api_key_from_step_4
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start the Frontend
```bash
npm run dev
```

Visit `http://localhost:3000`

## API Documentation

Once the backend is running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **Setup Info**: `http://localhost:8000/setup`
- **Health Check**: `http://localhost:8000/health`

## API Usage

### Example Request
```bash
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are tenant rights in India?", "language": "en"}'
```

### Response Format
```json
{
  "query": "What are tenant rights in India?",
  "language": "en",
  "response": "**Domain:** Property Law\n\n**Relevant Laws:** ...\n\n**Explanation:** ..."
}
```

## Troubleshooting

### Port 8000 Already in Use
If you have `main.py` running, stop it first:
```bash
# Find the process
netstat -ano | findstr :8000

# Kill it (Windows)
taskkill /PID <process_id> /F
```

### API Key Issues
- Check `.api_key` file in backend directory
- Or set `MCP_API_KEY` environment variable manually
- Visit `/setup` endpoint to view current key

### CORS Errors
Update `mcp_server.py` line 111 to include your frontend URL:
```python
allow_origins=["http://localhost:3000"],
```
