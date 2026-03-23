
## KnowYourStock — Finance assistant (FastAPI + LangGraph + Streamlit)

This repository implements a small finance-focused assistant that uses LangGraph workflows, LangChain-style LLMs, and a Streamlit UI for interactive exploration. It provides:

- A FastAPI server with endpoints to run LangGraph workflows and a chat interface.
- LangGraph workflows located in `Langgraph/` that orchestrate nodes in `nodes/` (news, screener, stock info, etc.).
- A Streamlit app (in `Streamlit KnowYourStock/`) for quick demos and UI.

This README explains how to run the FastAPI server and the Streamlit app, required environment variables, and where to find the main components.

## Repository layout (key files)

- `FastAPI_main.py` — FastAPI app exposing:
   - `GET /health` — health check
   - `POST /langgraph` — invoke the LangGraph workflow (optional body: `{ "stock_name": "AAPL" }`)
   - `POST /chat` — synchronous chat (body: `{ "message": "...", "context": {...}, "messages": [...] }`)
   - `POST /chat/stream` — streaming chat (SSE)
- `config.py` — loads environment variables and constructs LLM and API clients used by the app.
- `Models.py` — project Pydantic / state models.
- `Langgraph/` — contains `workflow.py`, `chat_workflow.py`, and helpers that define the graph-based workflows.
- `nodes/` — folder with node implementations used by the workflows (e.g., `News_node.py`, `ScreenerExtract_node.py`, `StockInfo_node.py`).
- `Streamlit KnowYourStock/app.py` — Streamlit demo UI.
- `requirements.txt` — Python dependencies.

## Requirements

- Python 3.10+ recommended
- On Windows PowerShell the example activation commands below are suitable.

## Quick setup (Windows PowerShell)

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

2. Create a `.env` file (project reads values via `python-dotenv` / `config.py`). Required/used variables (examples):

```env
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key
WEAVIATE_URL=https://your-weaviate-instance
WEAVIATE_API_KEY=your_weaviate_key

```

3. Run the FastAPI server (for local testing)

```powershell
# Option A: quick run (uses uvicorn programmatically)
python FastAPI_main.py

# Option B: use uvicorn directly
uvicorn FastAPI_main:app --host 0.0.0.0 --port 8000 --reload
```

4. Run the Streamlit demo UI

```powershell
streamlit run "Streamlit KnowYourStock/app.py"
```

## Example API usage

- Health check

   GET http://localhost:8000/health

- Run LangGraph workflow for a stock (POST /langgraph)

   Example body:

   ```json
   { "stock_name": "AAPL" }
   ```

   The endpoint will run the workflow that typically sequences the screener URL lookup and then nodes such as news, screener extract and stock info. It returns the aggregated state from the workflow.

- Chat endpoint (POST /chat)

   Example body:

   ```json
   {
      "message": "Tell me the latest about Apple",
      "context": { "User_stock_name": "Apple Inc.", "Stock_Ticker": "AAPL" },
      "messages": [ { "role":"user","content":"Hi" }, { "role":"assistant","content":"Hello" } ]
   }
   ```

- Streaming chat (POST /chat/stream)

   This endpoint returns a Server-Sent Events (SSE) stream containing incremental tokens from the LLM and a final `done` event with the updated message history.

## Notes and pointers

- The project uses a configured LLM client in `config.py` (variable `GEMINI_LLM`) and a Tavily client (`TAVILY_CLIENT`). Add API keys and other credentials to your `.env` before running.
- The LangGraph workflows are defined under `Langgraph/` and call functions in `nodes/`. Review those files to customize behavior or add new nodes.
- `Models.py` contains the Pydantic data models and chat state types used by `FastAPI_main.py`.

## Troubleshooting

- If you see import issues, ensure the workspace root is on PYTHONPATH or run the server from the repo root.
- For streaming SSE clients, use a browser or an SSE-capable client to connect to `/chat/stream`.

## Next steps / ideas

- Add a small Postman collection or OpenAPI examples for the endpoints.
- Add unit tests for core node logic and a CI step to run checks.

---

If you want, I can add an OpenAPI example file, a minimal Postman collection, or update the Streamlit README inside `Streamlit KnowYourStock/` next. 

