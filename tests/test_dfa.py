from backend.toc_engine.dfa import DFA


dfa = DFA(
    states={"q0", "q1"},

    alphabet={"0", "1"},

    transitions={
        "q0": {
            "0": "q0",
            "1": "q1"
        },
        "q1": {
            "0": "q1",
            "1": "q0"
        }
    },

    start_state="q0",

    final_states={"q0"}
)


result = dfa.simulate("1011")

print("Input:", result["input"])
print("Path:", " → ".join(result["path"]))
print("Accepted:", result["accepted"])