"""First and Follow set computations for LL(1) grammar.

These functions operate on a grammar-like object that exposes:
- productions: dict[lhs] -> list of rhs lists
- nonterminals: set of nonterminal symbols
- EPSILON: string used for epsilon
and mutable sets `first` and `follow` on the grammar instance.
"""
from typing import Set, List


def first_of_sequence(sequence: List[str], grammar) -> Set[str]:
    if not sequence:
        return {grammar.EPSILON}

    sequence_first = set()
    all_nullable = True
    for symbol in sequence:
        if symbol == grammar.EPSILON:
            sequence_first.add(grammar.EPSILON)
            break

        if symbol in grammar.nonterminals:
            symbol_first = grammar.first[symbol]
        else:
            symbol_first = {symbol}

        sequence_first |= (symbol_first - {grammar.EPSILON})

        if grammar.EPSILON not in symbol_first:
            all_nullable = False
            break

    if all_nullable:
        sequence_first.add(grammar.EPSILON)

    return sequence_first


def compute_first(grammar):
    changed = True
    while changed:
        changed = False
        for nonterminal, bodies in grammar.productions.items():
            for body in bodies:
                derived = first_of_sequence(body, grammar)
                before = len(grammar.first[nonterminal])
                grammar.first[nonterminal] |= derived
                if len(grammar.first[nonterminal]) != before:
                    changed = True


def compute_follow(grammar):
    grammar.follow[grammar.start_symbol].add(grammar.ENDMARKER)
    changed = True
    while changed:
        changed = False
        for lhs, bodies in grammar.productions.items():
            for body in bodies:
                for index, symbol in enumerate(body):
                    if symbol not in grammar.nonterminals:
                        continue

                    beta = body[index + 1:]
                    beta_first = first_of_sequence(beta, grammar)

                    before = len(grammar.follow[symbol])
                    grammar.follow[symbol] |= (beta_first - {grammar.EPSILON})
                    if grammar.EPSILON in beta_first or not beta:
                        grammar.follow[symbol] |= grammar.follow[lhs]

                    if len(grammar.follow[symbol]) != before:
                        changed = True
