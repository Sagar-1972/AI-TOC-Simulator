from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.toc_engine.dfa import DFA
from backend.toc_engine.nfa import NFA
from backend.toc_engine.enfa import ENFA
from backend.toc_engine.conversions import (
    enfa_to_nfa,
    nfa_to_dfa,
    enfa_to_dfa,
    minimize_dfa,
)
from backend.ai.gemini_helper import (
    generate_automaton_from_prompt,
    explain_simulation,
)


app = FastAPI(
    title="AI-TOC Simulator",
    description="Interactive Theory of Computation Simulation, Conversion & AI Platform",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, str]]
    start_state: str
    final_states: list[str]
    input: str = ""


class NFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    final_states: list[str]
    input: str = ""


class ENFASimulationRequest(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, list[str]]]
    start_state: str
    final_states: list[str]
    input: str = ""


class AIGenerateRequest(BaseModel):
    description: str
    automaton_type: str = "DFA"


class AIExplainRequest(BaseModel):
    automaton_type: str
    definition: dict[str, Any]
    simulation_result: dict[str, Any]


@app.get("/api")
@app.get("/api/")
@app.get("/api/health")
def root():
    return {
        "message": "AI-TOC Simulator API v2.1 is running",
        "modules": [
            "DFA", "NFA", "ENFA",
            "ENFA->NFA", "NFA->DFA", "ENFA->DFA", "DFA-Minimize",
            "Gemini-AI"
        ]
    }


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


@app.post("/api/convert/enfa-to-nfa")
@app.post("/convert/enfa-to-nfa")
def api_enfa_to_nfa(request: ENFASimulationRequest):
    try:
        return enfa_to_nfa(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/convert/nfa-to-dfa")
@app.post("/convert/nfa-to-dfa")
def api_nfa_to_dfa(request: NFASimulationRequest):
    try:
        return nfa_to_dfa(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/convert/enfa-to-dfa")
@app.post("/convert/enfa-to-dfa")
def api_enfa_to_dfa(request: ENFASimulationRequest):
    try:
        return enfa_to_dfa(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/convert/minimize-dfa")
@app.post("/convert/minimize-dfa")
def api_minimize_dfa(request: DFASimulationRequest):
    try:
        return minimize_dfa(
            states=request.states,
            alphabet=request.alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            final_states=request.final_states
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/ai/generate")
@app.post("/ai/generate")
def api_ai_generate(request: AIGenerateRequest):
    try:
        return generate_automaton_from_prompt(
            description=request.description,
            automaton_type=request.automaton_type
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/ai/explain")
@app.post("/ai/explain")
def api_ai_explain(request: AIExplainRequest):
    try:
        explanation = explain_simulation(
            automaton_type=request.automaton_type,
            definition=request.definition,
            simulation_result=request.simulation_result
        )
        return {"explanation": explanation}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
