from backend.toc_engine.nfa import NFA


# NFA that accepts strings containing "10"
nfa = NFA(
    states={"q0", "q1", "q2"},

    alphabet={"0", "1"},

    transitions={
        "q0": {
            "0": ["q0"],
            "1": ["q0", "q1"]
        },

        "q1": {
            "0": ["q2"],
            "1": []
        },

        "q2": {
            "0": ["q2"],
            "1": ["q2"]
        }
    },

    start_state="q0",

    final_states={"q2"}
)


# Test input
result = nfa.simulate("110")


print("Input:", result["input"])

print("Path:")

for step, states in enumerate(result["path"]):
    print(f"  Step {step}: {states}")

print("Accepted:", result["accepted"])