from collections import deque
from backend.toc_engine.dfa import DFA
from backend.toc_engine.nfa import NFA
from backend.toc_engine.enfa import ENFA


def enfa_to_nfa(states, alphabet, transitions, start_state, final_states):
    """
    Convert an ε-NFA into an equivalent NFA without ε-transitions
    using ε-closure(δ(ε-closure(q), a)).
    """
    enfa = ENFA(states, alphabet, transitions, start_state, final_states)
    enfa.validate()

    ordered_states = list(states)
    ordered_alphabet = [sym for sym in alphabet if sym != ENFA.EPSILON]

    closures = {
        q: sorted(enfa.epsilon_closure({q}))
        for q in ordered_states
    }

    nfa_transitions = {}
    steps = []

    for q in ordered_states:
        nfa_transitions[q] = {}
        q_closure = closures[q]
        for sym in ordered_alphabet:
            direct_targets = set()
            for p in q_closure:
                for dst in transitions.get(p, {}).get(sym, []):
                    direct_targets.add(dst)
            full_targets = sorted(enfa.epsilon_closure(direct_targets))
            nfa_transitions[q][sym] = full_targets
            steps.append({
                "state": q,
                "epsilon_closure": q_closure,
                "symbol": sym,
                "move_targets": sorted(direct_targets),
                "result_states": full_targets
            })

    start_closure = set(closures[start_state])
    nfa_finals = [
        q for q in ordered_states
        if set(closures[q]).intersection(set(final_states))
    ]

    # Validate constructed NFA
    NFA(ordered_states, ordered_alphabet, nfa_transitions, start_state, nfa_finals).validate()

    return {
        "states": ordered_states,
        "alphabet": ordered_alphabet,
        "transitions": nfa_transitions,
        "start_state": start_state,
        "final_states": nfa_finals,
        "epsilon_closures": closures,
        "steps": steps
    }


def nfa_to_dfa(states, alphabet, transitions, start_state, final_states):
    """
    Convert an NFA (or ε-NFA if ε transitions exist) into an equivalent DFA
    via Subset Construction.
    """
    has_epsilon = any(ENFA.EPSILON in transitions.get(q, {}) for q in states)
    if has_epsilon:
        nfa_data = enfa_to_nfa(states, alphabet, transitions, start_state, final_states)
        base_states = nfa_data["states"]
        base_alphabet = nfa_data["alphabet"]
        base_transitions = nfa_data["transitions"]
        base_start = nfa_data["start_state"]
        base_finals = set(nfa_data["final_states"])
    else:
        nfa = NFA(states, alphabet, transitions, start_state, final_states)
        nfa.validate()
        base_states = list(states)
        base_alphabet = list(alphabet)
        base_transitions = transitions
        base_start = start_state
        base_finals = set(final_states)

    def subset_name(subset_tuple):
        if not subset_tuple:
            return "∅"
        return "{" + ",".join(subset_tuple) + "}"

    start_subset = tuple(sorted([base_start]))
    queue = deque([start_subset])
    visited = {start_subset}
    dfa_transitions = {}
    subset_mapping = {}
    steps = []

    while queue:
        current_subset = queue.popleft()
        curr_label = subset_name(current_subset)
        subset_mapping[curr_label] = list(current_subset)
        dfa_transitions[curr_label] = {}

        for sym in base_alphabet:
            next_set = set()
            for q in current_subset:
                for dst in base_transitions.get(q, {}).get(sym, []):
                    next_set.add(dst)
            next_subset = tuple(sorted(next_set))
            next_label = subset_name(next_subset)
            dfa_transitions[curr_label][sym] = next_label
            steps.append({
                "from_subset": curr_label,
                "symbol": sym,
                "to_subset": next_label,
                "member_states": list(next_subset)
            })
            if next_subset not in visited:
                visited.add(next_subset)
                queue.append(next_subset)

    dfa_states = [subset_name(s) for s in visited]
    # Preserve deterministic order starting with start_subset
    ordered_subsets = [start_subset] + [s for s in visited if s != start_subset]
    dfa_states = [subset_name(s) for s in ordered_subsets]
    dfa_start = subset_name(start_subset)
    dfa_finals = [
        subset_name(s) for s in ordered_subsets
        if set(s).intersection(base_finals)
    ]

    DFA(dfa_states, base_alphabet, dfa_transitions, dfa_start, dfa_finals).validate()

    return {
        "states": dfa_states,
        "alphabet": base_alphabet,
        "transitions": dfa_transitions,
        "start_state": dfa_start,
        "final_states": dfa_finals,
        "subset_mapping": subset_mapping,
        "steps": steps
    }


def minimize_dfa(states, alphabet, transitions, start_state, final_states):
    """
    Minimize a DFA by removing unreachable states and partitioning equivalent states
    (Hopcroft / Table-Filling Partition Refinement).
    """
    dfa = DFA(states, alphabet, transitions, start_state, final_states)
    dfa.validate()

    ordered_alphabet = list(alphabet)
    # 1. Reachable states via BFS
    reachable = []
    seen = {start_state}
    q_bfs = deque([start_state])
    while q_bfs:
        curr = q_bfs.popleft()
        reachable.append(curr)
        for sym in ordered_alphabet:
            nxt = transitions[curr][sym]
            if nxt not in seen:
                seen.add(nxt)
                q_bfs.append(nxt)

    unreachable = [q for q in states if q not in seen]
    final_set = set(final_states)

    # 2. Initial partition: F and Q \ F
    f_group = tuple(sorted([q for q in reachable if q in final_set]))
    nf_group = tuple(sorted([q for q in reachable if q not in final_set]))

    partitions = []
    if f_group:
        partitions.append(f_group)
    if nf_group:
        partitions.append(nf_group)

    partition_history = [
        {
            "iteration": 0,
            "groups": [list(g) for g in partitions],
            "note": "Initial split into accepting (F) and non-accepting (Q \ F) reachable states"
        }
    ]

    iteration = 0
    while True:
        iteration += 1
        state_to_group = {}
        for idx, group in enumerate(partitions):
            for st in group:
                state_to_group[st] = idx

        new_partitions = []
        for group in partitions:
            if len(group) <= 1:
                new_partitions.append(group)
                continue
            buckets = {}
            for st in group:
                sig = tuple(state_to_group[transitions[st][sym]] for sym in ordered_alphabet)
                buckets.setdefault(sig, []).append(st)
            for b_states in buckets.values():
                new_partitions.append(tuple(sorted(b_states)))

        if set(new_partitions) == set(partitions):
            break

        partitions = new_partitions
        partition_history.append({
            "iteration": iteration,
            "groups": [list(g) for g in partitions],
            "note": f"Refinement round {iteration}: split distinguishable transition signatures"
        })

    # Order partitions so start_state's partition comes first
    start_part = next(g for g in partitions if start_state in g)
    ordered_parts = [start_part] + [g for g in partitions if g != start_part]

    def group_label(g):
        return g[0] if len(g) == 1 else "{" + ",".join(g) + "}"

    rep_to_label = {}
    group_mapping = {}
    for g in ordered_parts:
        lbl = group_label(g)
        group_mapping[lbl] = list(g)
        for st in g:
            rep_to_label[st] = lbl

    min_states = [group_label(g) for g in ordered_parts]
    min_start = rep_to_label[start_state]
    min_finals = [group_label(g) for g in ordered_parts if set(g).intersection(final_set)]
    min_transitions = {}
    for g in ordered_parts:
        lbl = group_label(g)
        rep = g[0]
        min_transitions[lbl] = {
            sym: rep_to_label[transitions[rep][sym]]
            for sym in ordered_alphabet
        }

    DFA(min_states, ordered_alphabet, min_transitions, min_start, min_finals).validate()

    return {
        "states": min_states,
        "alphabet": ordered_alphabet,
        "transitions": min_transitions,
        "start_state": min_start,
        "final_states": min_finals,
        "unreachable_removed": unreachable,
        "group_mapping": group_mapping,
        "partition_history": partition_history
    }


def regex_to_enfa(regex: str):
    """
    Convert a regular expression (supporting concatenation, |, *, +, ?, parentheses, and ε)
    into an ε-NFA using Thompson's Construction.
    """
    expr = regex.strip().replace(" ", "")
    if not expr:
        raise ValueError("Regular expression cannot be empty.")

    # Insert explicit concatenation operator '.'
    # Operators: | (union), . (concat), * (Kleene star), + (one or more), ? (optional)
    output_tokens = []
    unary_ops = {"*", "+", "?"}
    binary_ops = {"|", "."}
    all_ops = unary_ops | binary_ops | {"(", ")"}

    # Validate parentheses & characters
    bal = 0
    for ch in expr:
        if ch == "(":
            bal += 1
        elif ch == ")":
            bal -= 1
            if bal < 0:
                raise ValueError("Unbalanced parentheses in regular expression.")
        elif ch == ".":
            raise ValueError("Dot '.' is reserved for concatenation; use standard symbols.")
    if bal != 0:
        raise ValueError("Unbalanced parentheses in regular expression.")

    expanded = []
    for i, ch in enumerate(expr):
        expanded.append(ch)
        if i + 1 < len(expr):
            nxt = expr[i + 1]
            left_can_concat = (ch not in {"(", "|"})
            right_can_concat = (nxt not in {")", "|", "*", "+", "?"})
            if left_can_concat and right_can_concat:
                expanded.append(".")

    # Shunting-yard to postfix
    precedence = {"|": 1, ".": 2, "*": 3, "+": 3, "?": 3}
    postfix = []
    op_stack = []

    for tok in expanded:
        if tok not in all_ops:
            postfix.append(tok)
        elif tok == "(":
            op_stack.append(tok)
        elif tok == ")":
            while op_stack and op_stack[-1] != "(":
                postfix.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parentheses.")
            op_stack.pop()
        else:
            while op_stack and op_stack[-1] != "(" and precedence.get(op_stack[-1], 0) >= precedence[tok]:
                postfix.append(op_stack.pop())
            op_stack.append(tok)

    while op_stack:
        top = op_stack.pop()
        if top in {"(", ")"}:
            raise ValueError("Mismatched parentheses.")
        postfix.append(top)

    state_counter = 0
    transitions = {}
    alphabet = set()
    steps = []

    def new_state():
        nonlocal state_counter
        s = f"q{state_counter}"
        state_counter += 1
        transitions[s] = {}
        return s

    def add_edge(src, sym, dst):
        transitions.setdefault(src, {}).setdefault(sym, [])
        if dst not in transitions[src][sym]:
            transitions[src][sym].append(dst)

    nfa_stack = []
    for tok in postfix:
        if tok not in all_ops:
            s = new_state()
            e = new_state()
            sym = ENFA.EPSILON if tok in {"ε", "e"} and len(expr) == 1 else tok
            if sym != ENFA.EPSILON:
                alphabet.add(sym)
            add_edge(s, sym, e)
            nfa_stack.append((s, e))
            steps.append(f"Symbol '{sym}': created fragment ({s} --{sym}--> {e})")
        elif tok == ".":
            if len(nfa_stack) < 2:
                raise ValueError("Invalid concatenation in regular expression.")
            s2, e2 = nfa_stack.pop()
            s1, e1 = nfa_stack.pop()
            add_edge(e1, ENFA.EPSILON, s2)
            nfa_stack.append((s1, e2))
            steps.append(f"Concatenation: linked {e1} --ε--> {s2}")
        elif tok == "|":
            if len(nfa_stack) < 2:
                raise ValueError("Invalid union '|' in regular expression.")
            s2, e2 = nfa_stack.pop()
            s1, e1 = nfa_stack.pop()
            s = new_state()
            e = new_state()
            add_edge(s, ENFA.EPSILON, s1)
            add_edge(s, ENFA.EPSILON, s2)
            add_edge(e1, ENFA.EPSILON, e)
            add_edge(e2, ENFA.EPSILON, e)
            nfa_stack.append((s, e))
            steps.append(f"Union '|': branched {s} to ({s1}, {s2}) and merged into {e}")
        elif tok == "*":
            if not nfa_stack:
                raise ValueError("Invalid Kleene star '*' in regular expression.")
            s1, e1 = nfa_stack.pop()
            s = new_state()
            e = new_state()
            add_edge(s, ENFA.EPSILON, s1)
            add_edge(s, ENFA.EPSILON, e)
            add_edge(e1, ENFA.EPSILON, s1)
            add_edge(e1, ENFA.EPSILON, e)
            nfa_stack.append((s, e))
            steps.append(f"Kleene Star '*': wrapped ({s1}..{e1}) with loop and bypass ({s}..{e})")
        elif tok == "+":
            if not nfa_stack:
                raise ValueError("Invalid '+' operator in regular expression.")
            s1, e1 = nfa_stack.pop()
            s = new_state()
            e = new_state()
            add_edge(s, ENFA.EPSILON, s1)
            add_edge(e1, ENFA.EPSILON, s1)
            add_edge(e1, ENFA.EPSILON, e)
            nfa_stack.append((s, e))
            steps.append(f"Plus '+': wrapped ({s1}..{e1}) requiring >= 1 repetition ({s}..{e})")
        elif tok == "?":
            if not nfa_stack:
                raise ValueError("Invalid '?' operator in regular expression.")
            s1, e1 = nfa_stack.pop()
            s = new_state()
            e = new_state()
            add_edge(s, ENFA.EPSILON, s1)
            add_edge(s, ENFA.EPSILON, e)
            add_edge(e1, ENFA.EPSILON, e)
            nfa_stack.append((s, e))
            steps.append(f"Optional '?': added ε-bypass across ({s1}..{e1}) into ({s}..{e})")

    if len(nfa_stack) != 1:
        raise ValueError("Malformed regular expression.")

    start_state, final_state = nfa_stack[0]
    ordered_states = [f"q{i}" for i in range(state_counter)]
    ordered_alphabet = sorted(alphabet)

    for q in ordered_states:
        transitions.setdefault(q, {})
        transitions[q].setdefault(ENFA.EPSILON, [])
        for sym in ordered_alphabet:
            transitions[q].setdefault(sym, [])

    ENFA(ordered_states, ordered_alphabet, transitions, start_state, [final_state]).validate()

    return {
        "regex": expr,
        "states": ordered_states,
        "alphabet": ordered_alphabet,
        "transitions": transitions,
        "start_state": start_state,
        "final_states": [final_state],
        "steps": steps
    }
