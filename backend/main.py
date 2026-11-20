from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.toc_engine.dfa import DFA
from backend.toc_engine.nfa import NFA
from backend.toc_engine.enfa import ENFA


app = FastAPI(
    title="AI-TOC Simulator",
    description="Theory of Computation simulation API",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# REQUEST MODELS
# =========================

class DFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, str]]
    start_state: str
    final_states: list[str]
    input: str


class NFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    final_states: list[str]
    input: str


class ENFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    final_states: list[str]
    input: str


# =========================
# HEALTH / ROOT
# =========================

@app.get("/api")
@app.get("/api/")
@app.get("/api/health")
def root():
    return {
        "message": "AI-TOC Simulator API is running"
    }


# =========================
# DFA SIMULATION
# =========================

@app.post("/api/dfa/simulate")
@app.post("/dfa/simulate")
def simulate_dfa(request: DFASimulationRequest):
    try:
        dfa = DFA(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
        return dfa.simulate(request.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================
# NFA SIMULATION
# =========================

@app.post("/api/nfa/simulate")
@app.post("/nfa/simulate")
def simulate_nfa(request: NFASimulationRequest):
    try:
        nfa = NFA(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
        return nfa.simulate(request.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================
# ε-NFA SIMULATION
# =========================

@app.post("/api/enfa/simulate")
@app.post("/enfa/simulate")
def simulate_enfa(request: ENFASimulationRequest):
    try:
        enfa = ENFA(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
        return enfa.simulate(request.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
