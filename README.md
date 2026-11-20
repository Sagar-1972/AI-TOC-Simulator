# AI-TOC Simulator

Interactive Theory of Computation simulator supporting **DFA**, **NFA**, and **ε-NFA**, structured for one-click deployment on **Vercel**.

## Project Structure

- `frontend/` — Static HTML/CSS/JS simulator interfaces (`index.html`, `dfa.html`, `nfa.html`, `enfa.html`).
- `backend/` — FastAPI application and automata simulation engines (`DFA`, `NFA`, `ENFA`).
- `api/index.py` — Vercel Python Serverless Function entrypoint exposing the FastAPI app.
- `vercel.json` — Vercel build, static output, and `/api/*` rewrite configuration.
- `requirements.txt` — Python dependencies installed by Vercel during build.

## Deploying to Vercel

1. Push this repository to GitHub, GitLab, or Bitbucket (or import the folder directly with the Vercel CLI).
2. In Vercel, create a **New Project** pointing to this repository.
3. Leave Framework Preset as **Other** — Vercel automatically uses `vercel.json` to:
   - Copy `frontend/` into `public/` for static hosting at `/` (`index.html`, `/dfa.html`, `/nfa.html`, `/enfa.html`).
   - Deploy `api/index.py` as a Python Serverless Function handling `/api/*`.
4. Click **Deploy**.

## Running Locally

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Then serve `frontend/` (for example, `python -m http.server 5500 --directory frontend`) and open `http://127.0.0.1:5500`.
