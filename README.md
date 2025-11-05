# Finance-to-Tweet Assistant

Generate Twitter/X posts about financial news using AI, web search, and vector databases.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp config/env.example .env
# Edit .env with your API keys

# Run the app
streamlit run client/app.py
```

## Setup

1. Get API keys:
   - **Tavily**: https://tavily.com
   - **Gemini**: https://makersuite.google.com/app/apikey
   - **Weaviate**: https://weaviate.io/cloud

2. Create `.env` file:
```env
TAVILY_API_KEY=your_key
GEMINI_API_KEY=your_key
WEAVIATE_URL=your_url
WEAVIATE_API_KEY=your_key
```

## How It Works

1. User enters finance query → Search via Tavily
2. Content stored in Weaviate vector DB
3. LLM (Gemini) generates tweet using RAG
4. Display on Streamlit UI

## Files

- `server/mcp_server.py` - MCP server with 3 tools
- `client/app.py` - Streamlit UI
- `config/config.py` - Config loader

## MCP Tools

1. `search_web(query)` - Search Tavily
2. `store_content(content_json)` - Store in vector DB  
3. `generate_tweet(query, instructions)` - Generate tweet with RAG

## Run MCP Server Separately

```bash
python server/mcp_server.py
```

