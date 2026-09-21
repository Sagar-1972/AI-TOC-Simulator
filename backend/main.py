from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.toc_engine.dfa import DFA
from backend.toc_engine.nfa import NFA


app = FastAPI(
    title="AI-TOC Simulator",
    description="Theory of Computation simulation API",
    version="1.0.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DFA REQUEST MODEL
# =========================

class DFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, str]]
    start_state: str
    final_states: list[str]
    input: str


# =========================
# NFA REQUEST MODEL
# =========================

class NFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    final_states: list[str]
    input: str


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "AI-TOC Simulator API is running"
    }


# =========================
# DFA SIMULATION
# =========================

@app.post("/dfa/simulate")
def simulate_dfa(request: DFASimulationRequest):

    dfa = DFA(
        states=request.states,
        alphabet=request.alphabet,
        transitions=request.transitions,
        start_state=request.start_state,
        final_states=request.final_states
    )

    result = dfa.simulate(request.input)

    return result


# =========================
# NFA SIMULATION
# =========================

@app.post("/nfa/simulate")
def simulate_nfa(request: NFASimulationRequest):

    nfa = NFA(
        states=request.states,
        alphabet=request.alphabet,
        transitions=request.transitions,
        start_state=request.start_state,
        final_states=request.final_states
    )

    result = nfa.simulate(request.input)

    return result