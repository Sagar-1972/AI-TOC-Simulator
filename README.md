# AI-TOC Simulator v2.1

Interactive Theory of Computation learning platform ready for Vercel deployment.

## Modules

- **DFA Simulator** (`frontend/dfa.html` + `/api/dfa/simulate`) — Interactive step-by-step graph highlighting
- **NFA Simulator** (`frontend/nfa.html` + `/api/nfa/simulate`) — Nondeterministic state set playback
- **ε-NFA Simulator** (`frontend/enfa.html` + `/api/enfa/simulate`) — Epsilon-closure and transition visualization
- **Automata Conversions & Minimization** (`frontend/conversions.html` + `backend/toc_engine/conversions.py`):
  - **NFA → DFA** (`/api/convert/nfa-to-dfa`)
  - **ε-NFA → NFA** (`/api/convert/enfa-to-nfa`)
  - **ε-NFA → DFA** (`/api/convert/enfa-to-dfa`)
  - **DFA State Minimization** (`/api/convert/minimize-dfa`)
- **Gemini AI Studio** (`frontend/ai-assistant.html` + `/api/ai/generate`, `/api/ai/explain`)
