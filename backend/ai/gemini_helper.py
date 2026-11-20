import json
import os
import urllib.error
import urllib.request


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()


def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured in Vercel Environment Variables.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.25,
            "maxOutputTokens": 2048
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            candidates = body.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini returned an empty response.")
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts).strip()
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code}: {err_body}")


def generate_automaton_from_prompt(description: str, automaton_type: str = "DFA") -> dict:
    """
    Generate a complete DFA, NFA, or ε-NFA definition from natural language using Gemini.
    Returns structured JSON matching the simulator form fields.
    """
    atype = automaton_type.upper()
    if atype not in {"DFA", "NFA", "ENFA", "E-NFA", "Ε-NFA"}:
        atype = "DFA"
    if atype in {"E-NFA", "Ε-NFA"}:
        atype = "ENFA"

    prompt = f"""You are an expert Theory of Computation professor.
Design a minimal, mathematically valid {atype} for the following formal language description:
"{description}"

Return ONLY valid JSON (no markdown fences, no commentary) with this exact schema:
{{
  "automaton_type": "{atype}",
  "formal_language": "L = {{ ... }}",
  "states": ["q0", "q1"],
  "alphabet": ["0", "1"],
  "start_state": "q0",
  "final_states": ["q1"],
  "transitions_lines": [
    "q0,0,q0",
    "q0,1,q1"
  ],
  "sample_accept_input": "01",
  "sample_reject_input": "00",
  "explanation": "Clear 2-3 sentence explanation of what each state tracks."
}}

Formatting rules for transitions_lines:
- If DFA: every state MUST have one line `state,symbol,destination` for every symbol in alphabet.
- If NFA: use `state,symbol,dest1|dest2` (or leave destination empty `state,symbol,` if none).
- If ENFA: you may also use `ε` as a symbol (`q0,ε,q1`). Do NOT include `ε` in `alphabet`.
"""
    raw = _call_gemini(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    parsed = json.loads(cleaned)
    return parsed


def explain_simulation(automaton_type: str, definition: dict, simulation_result: dict) -> str:
    """
    Explain why an automaton accepted or rejected an input string step by step.
    """
    prompt = f"""You are a Theory of Computation tutor helping a Computer Science student.
Analyze this {automaton_type} simulation and explain clearly:
1. What formal language this {automaton_type} recognizes.
2. Step-by-step why the input "{simulation_result.get('input', '')}" was {"ACCEPTED" if simulation_result.get('accepted') else "REJECTED"}.
3. If rejected, give a short example string that WOULD be accepted.

Keep the explanation concise, clear, and well-structured using short bullet points.

Automaton Definition:
{json.dumps(definition, indent=2)}

Simulation Result:
{json.dumps(simulation_result, indent=2)}
"""
    return _call_gemini(prompt)
