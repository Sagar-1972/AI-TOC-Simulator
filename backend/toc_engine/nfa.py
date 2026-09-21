class NFA:
    def __init__(
        self,
        states,
        alphabet,
        transitions,
        start_state,
        final_states
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = set(final_states)

    def validate(self):
        """Validate the NFA definition."""

        if self.start_state not in self.states:
            raise ValueError(
                "Start state must be one of the states."
            )

        if not self.final_states.issubset(self.states):
            raise ValueError(
                "Final states must belong to the set of states."
            )

        for state in self.states:

            if state not in self.transitions:
                raise ValueError(
                    f"Missing transitions for state: {state}"
                )

            for symbol in self.alphabet:

                destinations = self.transitions[state].get(
                    symbol,
                    []
                )

                if not isinstance(destinations, list):
                    raise ValueError(
                        f"Transitions for {state}, {symbol} "
                        "must be a list."
                    )

                for destination in destinations:

                    if destination not in self.states:
                        raise ValueError(
                            f"Invalid destination state: "
                            f"{destination}"
                        )

        return True

    def simulate(self, input_string):
        """Simulate the NFA on an input string."""

        self.validate()

        current_states = {self.start_state}

        path = [
            sorted(current_states)
        ]

        for symbol in input_string:

            if symbol not in self.alphabet:
                return {
                    "accepted": False,
                    "reason": f"Invalid symbol: {symbol}",
                    "path": path
                }

            next_states = set()

            for state in current_states:

                destinations = (
                    self.transitions
                    .get(state, {})
                    .get(symbol, [])
                )

                for destination in destinations:
                    next_states.add(destination)

            current_states = next_states

            path.append(
                sorted(current_states)
            )

        accepted = bool(
            current_states.intersection(
                self.final_states
            )
        )

        return {
            "accepted": accepted,
            "final_states": sorted(current_states),
            "path": path,
            "input": input_string
        }