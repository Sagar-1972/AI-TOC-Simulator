from backend.toc_engine.enfa import ENFA


# ε-NFA example
#
# q0 --ε--> q1
# q1 --0--> q2
# q2 --1--> q3
#
# q3 is the final state.

enfa = ENFA(
    states={
        "q0",
        "q1",
        "q2",
        "q3"
    },

    alphabet={
        "0",
        "1"
    },

    transitions={
        "q0": {
            "ε": ["q1"],
            "0": [],
            "1": []
        },

        "q1": {
            "ε": [],
            "0": ["q2"],
            "1": []
        },

        "q2": {
            "ε": [],
            "0": [],
            "1": ["q3"]
        },

        "q3": {
            "ε": [],
            "0": [],
            "1": []
        }
    },

    start_state="q0",

    final_states={
        "q3"
    }
)


result = enfa.simulate("01")


print("Input:", result["input"])

print("Path:")

for step, item in enumerate(result["path"]):

    print(
        f"  Step {step}: "
        f"Input = {item['input']} "
        f"States = {item['states']}"
    )

print(
    "Accepted:",
    result["accepted"]
)