# AI-TOC Simulator v2.0

Full-featured, Vercel-ready Theory of Computation interactive learning platform.

## Included Modules

### Finite Automata (with Interactive Step-by-Step Graph Highlighting)
- `frontend/dfa.html` — Deterministic Finite Automaton simulator
- `frontend/nfa.html` — Non-Deterministic Finite Automaton simulator
- `frontend/enfa.html` — Epsilon-NFA simulator with ε-closure computation

### Automata Conversions & Minimization (`backend/toc_engine/conversions.py` + `frontend/conversions.html`)
- **NFA → DFA** (Subset Construction)
- **ε-NFA → NFA** (ε-closure elimination)
- **DFA State Minimization** (Unreachable state pruning + Partition Refinement)
- **Regex → ε-NFA** (Thompson's Construction)

### Advanced Computation Models (`backend/toc_engine/pda_tm.py`)
- `frontend/pda.html` — Pushdown Automaton (PDA) with live stack frame tracing
- `frontend/tm.html` — Single-Tape Turing Machine with interactive tape head stepping

### Google Gemini AI Integration (`backend/ai/gemini_helper.py` + `frontend/ai-assistant.html`)
- Natural-language to DFA/NFA/ε-NFA generator (`/api/ai/generate`)
- Step-by-step simulation explainer (`/api/ai/explain`)
- Set `GEMINI_API_KEY` in **Vercel Project Settings → Environment Variables** to enable live AI generation.
