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

    nfa_finals = [
        q for q in ordered_states
        if set(closures[q]).intersection(set(final_states))
    ]

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
    Convert an NFA into an equivalent DFA via Subset Construction.
    """
    nfa = NFA(states, alphabet, transitions, start_state, final_states)
    nfa.validate()
    base_alphabet = list(alphabet)
    base_finals = set(final_states)

    def subset_name(subset_tuple):
        if not subset_tuple:
            return "∅"
        return "{" + ",".join(subset_tuple) + "}"

    start_subset = tuple(sorted([start_state]))
    queue = deque([start_subset])
    visited = {start_subset}
    ordered_subsets = [start_subset]
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
                for dst in transitions.get(q, {}).get(sym, []):
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
                ordered_subsets.append(next_subset)
                queue.append(next_subset)

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


def enfa_to_dfa(states, alphabet, transitions, start_state, final_states):
    """
    Convert an ε-NFA directly into an equivalent DFA using ε-closure + Subset Construction:
      Start state = ε-closure({q0})
      δ_DFA(T, a) = ε-closure(⋃_{q ∈ T} δ(q, a))
    """
    enfa = ENFA(states, alphabet, transitions, start_state, final_states)
    enfa.validate()

    ordered_states = list(states)
    ordered_alphabet = [sym for sym in alphabet if sym != ENFA.EPSILON]
    base_finals = set(final_states)

    closures = {
        q: sorted(enfa.epsilon_closure({q}))
        for q in ordered_states
    }

    def subset_name(subset_tuple):
        if not subset_tuple:
            return "∅"
        return "{" + ",".join(subset_tuple) + "}"

    start_subset = tuple(sorted(enfa.epsilon_closure({start_state})))
    queue = deque([start_subset])
    visited = {start_subset}
    ordered_subsets = [start_subset]
    dfa_transitions = {}
    subset_mapping = {}
    steps = []

    while queue:
        current_subset = queue.popleft()
        curr_label = subset_name(current_subset)
        subset_mapping[curr_label] = list(current_subset)
        dfa_transitions[curr_label] = {}

        for sym in ordered_alphabet:
            move_set = set()
            for q in current_subset:
                for dst in transitions.get(q, {}).get(sym, []):
                    move_set.add(dst)
            next_closure = tuple(sorted(enfa.epsilon_closure(move_set)))
            next_label = subset_name(next_closure)
            dfa_transitions[curr_label][sym] = next_label
            steps.append({
                "from_subset": curr_label,
                "symbol": sym,
                "move_states": sorted(move_set),
                "to_subset": next_label,
                "member_states": list(next_closure)
            })
            if next_closure not in visited:
                visited.add(next_closure)
                ordered_subsets.append(next_closure)
                queue.append(next_closure)

    dfa_states = [subset_name(s) for s in ordered_subsets]
    dfa_start = subset_name(start_subset)
    dfa_finals = [
        subset_name(s) for s in ordered_subsets
        if set(s).intersection(base_finals)
    ]

    DFA(dfa_states, ordered_alphabet, dfa_transitions, dfa_start, dfa_finals).validate()

    return {
        "states": dfa_states,
        "alphabet": ordered_alphabet,
        "transitions": dfa_transitions,
        "start_state": dfa_start,
        "final_states": dfa_finals,
        "epsilon_closures": closures,
        "subset_mapping": subset_mapping,
        "steps": steps
    }


def minimize_dfa(states, alphabet, transitions, start_state, final_states):
    """
    Minimize a DFA by removing unreachable states and partitioning equivalent states
    (Partition Refinement).
    """
    dfa = DFA(states, alphabet, transitions, start_state, final_states)
    dfa.validate()

    ordered_alphabet = list(alphabet)
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
