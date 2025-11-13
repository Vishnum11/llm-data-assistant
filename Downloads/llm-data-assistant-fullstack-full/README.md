# LLM Data Assistant — Fullstack (FastAPI + React)

This repo provides a fullstack example:
- FastAPI backend (file ingest, projects, auth, chat)
- Chroma local vectorstore per project
- React frontend (upload, create projects, chat)
- Tests + GitHub Actions CI
- Dockerfile + docker-compose for local running

## Quick start (local)

1. Copy repo and set env:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export SECRET_KEY="your-secret"
   ```

2. Start backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. Start frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. Register in frontend, create a project, upload `sample_data.csv`, then ask questions.

## Notes
- The app uses OpenAI; set OPENAI_API_KEY before running.
- Replace auth flow with production-ready OAuth2 when moving to production.
- For CI without calling OpenAI, mock OpenAI calls in tests.
