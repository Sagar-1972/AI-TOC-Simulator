class ENFA:
    EPSILON = "ε"

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
        """Validate the ε-NFA definition."""

        if self.start_state not in self.states:
            raise ValueError(
                "Start state must be one of the states."
            )

        if not self.final_states.issubset(self.states):
            raise ValueError(
                "Final states must belong to the set of states."
            )

        if self.EPSILON in self.alphabet:
            raise ValueError(
                "ε must not be included in the input alphabet."
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

            epsilon_destinations = self.transitions[state].get(
                self.EPSILON,
                []
            )

            if not isinstance(epsilon_destinations, list):
                raise ValueError(
                    f"ε transitions for {state} must be a list."
                )

            for destination in epsilon_destinations:

                if destination not in self.states:
                    raise ValueError(
                        f"Invalid ε destination state: "
                        f"{destination}"
                    )

        return True

    def epsilon_closure(self, states):
        """
        Find all states reachable using only ε transitions.
        """

        closure = set(states)

        stack = list(states)

        while stack:

            current_state = stack.pop()

            epsilon_destinations = (
                self.transitions
                .get(current_state, {})
                .get(self.EPSILON, [])
            )

            for destination in epsilon_destinations:

                if destination not in closure:

                    closure.add(destination)

                    stack.append(destination)

        return closure

    def simulate(self, input_string):
        """Simulate the ε-NFA on an input string."""

        self.validate()

        current_states = self.epsilon_closure(
            {self.start_state}
        )

        path = [
            {
                "input": "ε",
                "states": sorted(current_states)
            }
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

            current_states = self.epsilon_closure(
                next_states
            )

            path.append(
                {
                    "input": symbol,
                    "states": sorted(current_states)
                }
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