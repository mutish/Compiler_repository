from computations import first_of_sequence, compute_first, compute_follow


class LL1Grammar:
    """Owns grammar preparation and LL(1) analysis artifacts."""

    EPSILON = "epsilon"
    ENDMARKER = "EOF"

    def __init__(self):
        self.start_symbol = "<program>"
        # Grammar is already written in a right-recursive, left-factored shape.
        self.productions = {
            "<program>": [["<stmt_list>"]],
            "<stmt_list>": [["<stmt>", "<stmt_list_prime>"]],
            "<stmt_list_prime>": [["<stmt>", "<stmt_list_prime>"], [self.EPSILON]],
            "<stmt>": [["<assignment>"], ["<if_stmt>"], ["<while_stmt>"]],
            "<assignment>": [["ID", "=", "<expr>"]],
            # Without INDENT/DEDENT tokens, control-flow bodies are one statement.
            "<if_stmt>": [["if", "<cond>", ":", "<stmt>", "else", ":", "<stmt>"]],
            "<while_stmt>": [["while", "<cond>", ":", "<stmt>"]],
            "<cond>": [["<expr>", "RELOP", "<expr>"]],
            "<expr>": [["<term>", "<expr_prime>"]],
            "<expr_prime>": [["+", "<expr>"], ["-", "<expr>"], [self.EPSILON]],
            "<term>": [["ID"], ["NUM"], ["STR"]],
        }

        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {symbol: set() for symbol in self.nonterminals}
        self.follow = {symbol: set() for symbol in self.nonterminals}
        self.parsing_table = {symbol: {} for symbol in self.nonterminals}

    def _collect_terminals(self):
        terminals = set()
        for bodies in self.productions.values():
            for body in bodies:
                for symbol in body:
                    if symbol not in self.productions and symbol != self.EPSILON:
                        terminals.add(symbol)
        terminals.add(self.ENDMARKER)
        terminals.add(self.EPSILON)
        return terminals

    def _eliminate_direct_left_recursion(self):
        """Applies the standard A->Aalpha|beta rewrite when needed."""
        new_productions = {}
        for nonterminal, bodies in self.productions.items():
            recursive = []
            non_recursive = []
            for body in bodies:
                if body and body[0] == nonterminal:
                    recursive.append(body[1:])
                else:
                    non_recursive.append(body)

            if not recursive:
                new_productions[nonterminal] = bodies
                continue

            helper = f"{nonterminal}_tail"
            new_non_recursive = []
            for body in non_recursive:
                if body == [self.EPSILON]:
                    new_non_recursive.append([helper])
                else:
                    new_non_recursive.append(body + [helper])

            helper_bodies = [alpha + [helper] for alpha in recursive]
            helper_bodies.append([self.EPSILON])

            new_productions[nonterminal] = new_non_recursive
            new_productions[helper] = helper_bodies

        self.productions = new_productions

    def _left_factor(self):
        """Performs one-symbol left factoring repeatedly until stable."""
        counter = {}
        changed = True
        while changed:
            changed = False
            updated = {}
            for nonterminal, bodies in self.productions.items():
                prefix_groups = {}
                for body in bodies:
                    first_symbol = body[0] if body else self.EPSILON
                    prefix_groups.setdefault(first_symbol, []).append(body)

                factor_symbol = None
                factor_group = None
                for symbol, grouped in prefix_groups.items():
                    if symbol != self.EPSILON and len(grouped) > 1:
                        factor_symbol = symbol
                        factor_group = grouped
                        break

                if factor_group is None:
                    updated[nonterminal] = bodies
                    continue

                changed = True
                if nonterminal not in counter:
                    counter[nonterminal] = 0
                counter[nonterminal] += 1
                helper = f"{nonterminal}_factored_{counter[nonterminal]}"
                suffixes = []
                remaining = []

                for body in bodies:
                    if body in factor_group:
                        suffix = body[1:] if len(body) > 1 else [self.EPSILON]
                        suffixes.append(suffix)
                    else:
                        remaining.append(body)

                remaining.append([factor_symbol, helper])
                updated[nonterminal] = remaining
                updated[helper] = suffixes

            self.productions = updated
            self.nonterminals = set(self.productions.keys())

    def prepare(self):
        self._eliminate_direct_left_recursion()
        self._left_factor()
        self.nonterminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        self.first = {symbol: set() for symbol in self.nonterminals}
        self.follow = {symbol: set() for symbol in self.nonterminals}
        self.parsing_table = {symbol: {} for symbol in self.nonterminals}

    def _first_of_sequence(self, sequence):
        return first_of_sequence(sequence, self)

    def compute_first(self):
        compute_first(self)

    def compute_follow(self):
        compute_follow(self)

    def build_table(self):
        conflicts = []
        for lhs, bodies in self.productions.items():
            for body in bodies:
                first_body = self._first_of_sequence(body)
                lookaheads = set(first_body - {self.EPSILON})
                if self.EPSILON in first_body:
                    lookaheads |= self.follow[lhs]

                for terminal in lookaheads:
                    existing = self.parsing_table[lhs].get(terminal)
                    if existing is not None and existing != body:
                        conflicts.append((lhs, terminal, existing, body))
                    else:
                        self.parsing_table[lhs][terminal] = body

        return conflicts
