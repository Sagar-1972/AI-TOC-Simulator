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
    minimize_dfa,
    regex_to_enfa,
)
from backend.toc_engine.pda_tm import PDA, TuringMachine
from backend.ai.gemini_helper import (
    generate_automaton_from_prompt,
    explain_simulation,
)


app = FastAPI(
    title="AI-TOC Simulator",
    description="Interactive Theory of Computation Simulation, Conversion & AI Platform",
    version="2.0.0"
)

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


class RegexRequest(BaseModel):
    regex: str


class PDASimulationRequest(BaseModel):
    states: list[str]
    input_alphabet: list[str]
    stack_alphabet: list[str]
    transitions: dict[str, Any]
    start_state: str
    start_stack: str
    final_states: list[str]
    acceptance_mode: str = "final_state"
    input: str


class TMSimulationRequest(BaseModel):
    states: list[str]
    input_alphabet: list[str]
    tape_alphabet: list[str]
    blank_symbol: str = "_"
    transitions: dict[str, dict[str, dict[str, str]]]
    start_state: str
    accept_states: list[str]
    reject_states: list[str] = []
    input: str


class AIGenerateRequest(BaseModel):
    description: str
    automaton_type: str = "DFA"


class AIExplainRequest(BaseModel):
    automaton_type: str
    definition: dict[str, Any]
    simulation_result: dict[str, Any]


# =========================
# HEALTH / ROOT
# =========================

@app.get("/api")
@app.get("/api/")
@app.get("/api/health")
def root():
    return {
        "message": "AI-TOC Simulator API v2.0 is running",
        "modules": [
            "DFA", "NFA", "ENFA",
            "ENFA->NFA", "NFA->DFA", "DFA-Minimize", "Regex->ENFA",
            "PDA", "TuringMachine", "Gemini-AI"
        ]
    }


# =========================
# FINITE AUTOMATA SIMULATION
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


# =========================
# AUTOMATA CONVERSIONS & MINIMIZATION
# =========================

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


@app.post("/api/convert/regex-to-enfa")
@app.post("/convert/regex-to-enfa")
def api_regex_to_enfa(request: RegexRequest):
    try:
        return regex_to_enfa(request.regex)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================
# PDA & TURING MACHINE
# =========================

@app.post("/api/pda/simulate")
@app.post("/pda/simulate")
def simulate_pda(request: PDASimulationRequest):
    try:
        pda = PDA(
            states=request.states,
            input_alphabet=request.input_alphabet,
            stack_alphabet=request.stack_alphabet,
            transitions=request.transitions,
            start_state=request.start_state,
            start_stack=request.start_stack,
            final_states=request.final_states,
            acceptance_mode=request.acceptance_mode
        )
        return pda.simulate(request.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/tm/simulate")
@app.post("/tm/simulate")
def simulate_tm(request: TMSimulationRequest):
    try:
        tm = TuringMachine(
            states=request.states,
            input_alphabet=request.input_alphabet,
            tape_alphabet=request.tape_alphabet,
            blank_symbol=request.blank_symbol,
            transitions=request.transitions,
            start_state=request.start_state,
            accept_states=request.accept_states,
            reject_states=request.reject_states
        )
        return tm.simulate(request.input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================
# GEMINI AI ASSISTANT
# =========================

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
