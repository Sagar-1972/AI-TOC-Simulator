from collections import deque


class PDA:
    """
    Non-deterministic Pushdown Automaton (Acceptance by Final State or Empty Stack).
    Transition format:
      transitions[state][input_symbol_or_eps][stack_top_or_eps] = [
          {"next_state": "q1", "push": ["A", "Z"]}
      ]
    """
    EPSILON = "ε"

    def __init__(self, states, input_alphabet, stack_alphabet, transitions, start_state, start_stack, final_states, acceptance_mode="final_state"):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.start_stack = start_stack
        self.final_states = set(final_states)
        self.acceptance_mode = acceptance_mode

    def validate(self):
        if self.start_state not in self.states:
            raise ValueError("Start state must belong to states.")
        if self.start_stack not in self.stack_alphabet:
            raise ValueError("Initial stack symbol must belong to stack alphabet.")
        if not self.final_states.issubset(self.states):
            raise ValueError("Final states must belong to states.")
        if self.acceptance_mode not in {"final_state", "empty_stack"}:
            raise ValueError("Acceptance mode must be 'final_state' or 'empty_stack'.")
        return True

    def simulate(self, input_string: str, max_steps: int = 2500):
        self.validate()
        for ch in input_string:
            if ch not in self.input_alphabet:
                return {
                    "accepted": False,
                    "reason": f"Invalid input symbol: '{ch}'",
                    "trace": []
                }

        # State in BFS: (state, index_in_input, stack_tuple, trace_list)
        init_stack = (self.start_stack,)
        init_trace = [{
            "step": 0,
            "state": self.start_state,
            "remaining_input": input_string if input_string else "ε",
            "stack": list(init_stack),
            "action": "Start configuration"
        }]

        queue = deque([(self.start_state, 0, init_stack, init_trace)])
        visited = {(self.start_state, 0, init_stack)}
        explored = 0
        best_trace = init_trace

        while queue and explored < max_steps:
            state, idx, stack, trace = queue.popleft()
            explored += 1
            if len(trace) > len(best_trace):
                best_trace = trace

            if idx == len(input_string):
                if self.acceptance_mode == "final_state" and state in self.final_states:
                    return {
                        "accepted": True,
                        "final_state": state,
                        "final_stack": list(stack),
                        "trace": trace,
                        "input": input_string
                    }
                if self.acceptance_mode == "empty_stack" and len(stack) == 0:
                    return {
                        "accepted": True,
                        "final_state": state,
                        "final_stack": [],
                        "trace": trace,
                        "input": input_string
                    }

            state_rules = self.transitions.get(state, {})
            possible_inputs = [self.EPSILON]
            if idx < len(input_string):
                possible_inputs.append(input_string[idx])

            top_symbol = stack[0] if stack else self.EPSILON
            possible_tops = [self.EPSILON]
            if stack:
                possible_tops.append(top_symbol)

            for in_sym in possible_inputs:
                sym_rules = state_rules.get(in_sym, {})
                for pop_sym in possible_tops:
                    rules = sym_rules.get(pop_sym, [])
                    for rule in rules:
                        nxt_state = rule["next_state"]
                        if nxt_state not in self.states:
                            raise ValueError(f"Invalid destination state: {nxt_state}")
                        push_syms = rule.get("push", [])
                        for ps in push_syms:
                            if ps != self.EPSILON and ps not in self.stack_alphabet:
                                raise ValueError(f"Invalid stack symbol pushed: {ps}")

                        rem_stack = stack[1:] if pop_sym != self.EPSILON else stack
                        pushed_clean = tuple(s for s in push_syms if s != self.EPSILON)
                        new_stack = pushed_clean + rem_stack
                        if len(new_stack) > 80:
                            continue

                        new_idx = idx + (1 if in_sym != self.EPSILON else 0)
                        config = (nxt_state, new_idx, new_stack)
                        if config not in visited:
                            visited.add(config)
                            rem_in = input_string[new_idx:] if new_idx < len(input_string) else "ε"
                            push_disp = "".join(pushed_clean) if pushed_clean else "ε"
                            new_trace = trace + [{
                                "step": len(trace),
                                "state": nxt_state,
                                "remaining_input": rem_in,
                                "stack": list(new_stack),
                                "action": f"δ({state}, {in_sym}, {pop_sym}) → ({nxt_state}, {push_disp})"
                            }]
                            queue.append((nxt_state, new_idx, new_stack, new_trace))

        return {
            "accepted": False,
            "reason": (
                "No accepting computation path reached a final state."
                if self.acceptance_mode == "final_state"
                else "No computation path emptied the stack at end of input."
            ),
            "trace": best_trace,
            "input": input_string
        }


class TuringMachine:
    """
    Deterministic Single-Tape Turing Machine simulator.
    transitions[state][read_symbol] = {
        "next_state": "q1",
        "write": "X",
        "move": "R"  # L, R, or S
    }
    """
    def __init__(self, states, input_alphabet, tape_alphabet, blank_symbol, transitions, start_state, accept_states, reject_states=None):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.blank_symbol = blank_symbol
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states or [])

    def validate(self):
        if self.start_state not in self.states:
            raise ValueError("Start state must belong to states.")
        if self.blank_symbol not in self.tape_alphabet:
            raise ValueError("Blank symbol must belong to tape alphabet.")
        if not self.accept_states.issubset(self.states):
            raise ValueError("Accept states must belong to states.")
        if not self.reject_states.issubset(self.states):
            raise ValueError("Reject states must belong to states.")
        return True

    def simulate(self, input_string: str, max_steps: int = 500):
        self.validate()
        for ch in input_string:
            if ch not in self.input_alphabet:
                return {
                    "accepted": False,
                    "halted": True,
                    "reason": f"Invalid input symbol: '{ch}'",
                    "trace": []
                }

        tape = {}
        for i, ch in enumerate(input_string):
            tape[i] = ch
        if not tape:
            tape[0] = self.blank_symbol

        head = 0
        state = self.start_state

        def snapshot_tape(curr_head):
            min_idx = min(min(tape.keys()), curr_head) - 1
            max_idx = max(max(tape.keys()), curr_head) + 1
            cells = []
            for idx in range(min_idx, max_idx + 1):
                cells.append({
                    "index": idx,
                    "symbol": tape.get(idx, self.blank_symbol),
                    "head": idx == curr_head
                })
            return cells

        trace = [{
            "step": 0,
            "state": state,
            "head": head,
            "read": tape.get(head, self.blank_symbol),
            "action": "Initial tape",
            "tape": snapshot_tape(head)
        }]

        for step in range(1, max_steps + 1):
            if state in self.accept_states:
                return {
                    "accepted": True,
                    "halted": True,
                    "final_state": state,
                    "steps_taken": step - 1,
                    "trace": trace,
                    "input": input_string
                }
            if state in self.reject_states:
                return {
                    "accepted": False,
                    "halted": True,
                    "final_state": state,
                    "reason": f"Halted in explicit reject state {state}.",
                    "steps_taken": step - 1,
                    "trace": trace,
                    "input": input_string
                }

            read_sym = tape.get(head, self.blank_symbol)
            rule = self.transitions.get(state, {}).get(read_sym)
            if not rule:
                return {
                    "accepted": False,
                    "halted": True,
                    "final_state": state,
                    "reason": f"No transition defined for δ({state}, {read_sym}). Machine halted.",
                    "steps_taken": step - 1,
                    "trace": trace,
                    "input": input_string
                }

            nxt_state = rule["next_state"]
            write_sym = rule["write"]
            move_dir = rule["move"].upper()

            if nxt_state not in self.states:
                raise ValueError(f"Invalid destination state: {nxt_state}")
            if write_sym not in self.tape_alphabet:
                raise ValueError(f"Invalid tape symbol written: {write_sym}")
            if move_dir not in {"L", "R", "S"}:
                raise ValueError(f"Invalid head direction '{move_dir}'. Use L, R, or S.")

            tape[head] = write_sym
            if move_dir == "R":
                head += 1
            elif move_dir == "L":
                head -= 1

            prev_state = state
            state = nxt_state
            trace.append({
                "step": step,
                "state": state,
                "head": head,
                "read": tape.get(head, self.blank_symbol),
                "action": f"δ({prev_state}, {read_sym}) → ({nxt_state}, {write_sym}, {move_dir})",
                "tape": snapshot_tape(head)
            })

            if state in self.accept_states:
                return {
                    "accepted": True,
                    "halted": True,
                    "final_state": state,
                    "steps_taken": step,
                    "trace": trace,
                    "input": input_string
                }
            if state in self.reject_states:
                return {
                    "accepted": False,
                    "halted": True,
                    "final_state": state,
                    "reason": f"Halted in explicit reject state {state}.",
                    "steps_taken": step,
                    "trace": trace,
                    "input": input_string
                }

        return {
            "accepted": False,
            "halted": False,
            "final_state": state,
            "reason": f"Exceeded step limit ({max_steps} steps) — possible infinite loop.",
            "steps_taken": max_steps,
            "trace": trace,
            "input": input_string
        }
