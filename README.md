# AI PM Assistant

An AI tool that generates PRDs, user stories, and MoSCoW prioritization for product managers. Built it to explore how RAG + LLMs can speed up early-stage PM work - you give it a product name and description, it gives you structured docs you'd normally spend hours writing.

**Live demo:** https://ai-pm-assistant-livid.vercel.app

## What it does

- Generates a full PRD (Problem Statement, Goals, Personas, Features, Scope, Timeline) from a short product description
- Generates 8 user stories in standard "As a [user], I want to..." format
- Generates MoSCoW prioritization (Must/Should/Could/Won't Have)
- Lets you upload past PRDs/specs so the assistant can retrieve relevant context and match your team's writing style (RAG)
- Saves generation history and lets you download any doc as a PDF

## Tech stack

- **Backend:** FastAPI (Python)
- **LLM:** Groq API, running Llama 3.3-70B
- **RAG:** ChromaDB for vector storage + `sentence-transformers` (all-MiniLM-L6-v2) for embeddings
- **Database:** SQLite + SQLAlchemy
- **Frontend:** HTML/CSS/JS
- **Deployment:** Dockerized backend, frontend on Vercel

## How it works

When you upload a document, it gets split into chunks and embedded into ChromaDB. When you generate a PRD/user stories/prioritization, your input gets embedded too, the most relevant chunks are pulled back via vector similarity search, and that context gets stuffed into the system prompt before it's sent to Groq. The output gets saved to SQLite so it shows up in `/history`, and you can pull it back down as a PDF anytime.

If ChromaDB/sentence-transformers aren't available for some reason (e.g. missing deps in a stripped-down deploy), the app doesn't crash — it just skips retrieval and generates without context.

## API endpoints

- `POST /generate` — generate a PRD
- `POST /user-stories` — generate 8 user stories
- `POST /prioritize` — generate MoSCoW prioritization
- `POST /upload` — upload a doc for RAG context
- `DELETE /clear-documents` — wipe uploaded RAG documents
- `GET /history` — see everything you've generated
- `GET /download/{doc_id}` — download a doc as PDF

## Running it locally

```bash
git clone https://github.com/Tanisha251204/ai-pm-assistant.git
cd ai-pm-assistant
pip install -r requirements.txt
```

Add a `.env` file with your Groq key:
```
GROQ_API_KEY=your_key_here
```

Then run:
```bash
uvicorn main:app --reload
```

Backend runs on `localhost:8000`. Open `frontend/index.html` to use the UI, or hit the API directly.

## Known limitations

- Chunking is fixed-size (500 chars, no overlap) — not the most retrieval-friendly approach, works fine for small docs
- No auth on the API — it's a demo, not meant to be public-facing as-is
- CORS is wide open (`*`) for now
- SQLite works fine for single-user/demo use but wouldn't hold up under real concurrent load

## What I'd add next

- Better chunking (token-aware, with overlap)
- Basic auth on the endpoints
- Swap SQLite for Postgres if this ever needed to handle multiple users at once
