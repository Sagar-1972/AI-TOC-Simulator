class DFA:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = set(final_states)

    def validate(self):
        """Validate the DFA definition."""

        if self.start_state not in self.states:
            raise ValueError("Start state must be one of the states.")

        if not self.final_states.issubset(self.states):
            raise ValueError("Final states must belong to the set of states.")

        for state in self.states:
            if state not in self.transitions:
                raise ValueError(f"Missing transitions for state: {state}")

            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    raise ValueError(
                        f"Missing transition: δ({state}, {symbol})"
                    )

                destination = self.transitions[state][symbol]

                if destination not in self.states:
                    raise ValueError(
                        f"Invalid destination state: {destination}"
                    )

        return True

    def simulate(self, input_string):
        """Run the DFA on an input string."""

        self.validate()

        current_state = self.start_state
        path = [current_state]

        for symbol in input_string:

            if symbol not in self.alphabet:
                return {
                    "accepted": False,
                    "reason": f"Invalid symbol: {symbol}",
                    "path": path
                }

            current_state = self.transitions[current_state][symbol]
            path.append(current_state)

        return {
            "accepted": current_state in self.final_states,
            "final_state": current_state,
            "path": path,
            "input": input_string
        }