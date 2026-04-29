from lexer import Scanner
from tokens import Token
from grammar import LL1Grammar


class ParseTreeNode:
    """A simple n-ary tree node to represent the parse tree."""
    def __init__(self, symbol):
        self.symbol = symbol
        self.lexeme = None
        self.children = []

    def print_tree(self, prefix="", is_last=True, is_root=True):
        lexeme_str = f"('{self.lexeme}')" if self.lexeme else ""
        node_display = f"{self.symbol}{lexeme_str}"

        if is_root:
            print(node_display)
            new_prefix = prefix
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node_display}")
            new_prefix = prefix + ("    " if is_last else "│   ")

        #print all children recursively
        child_count = len(self.children)
        for i, child in enumerate(self.children):
            child_is_last = (i == child_count - 1)
            child.print_tree(new_prefix, child_is_last, is_root=False)




class Parser:
    """
    Table-driven LL(1) Predictive Parser (Method B).
    Validates syntax using an explicit stack and an LL(1) parsing table.
    """
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.current_token = self.scanner.get_next_token()
        self.root = ParseTreeNode("<program>")
        self.errors = []

        self.grammar = LL1Grammar()
        self.grammar.prepare()
        self.grammar.compute_first()
        self.grammar.compute_follow()
        conflicts = self.grammar.build_table()
        if conflicts:
            details = []
            for lhs, lookahead, old_body, new_body in conflicts:
                details.append(
                    f"M[{lhs}, {lookahead}] has {old_body} and {new_body}"
                )
            raise ValueError("Grammar is not LL(1): " + "; ".join(details))

        # The explicit stack stores (grammar_symbol, parse_tree_node).
        self.stack = [(self.grammar.ENDMARKER, None), (self.grammar.start_symbol, self.root)]

    def _get_terminal_key(self, token: Token) -> str:
        """Maps lexer tokens to grammar terminal symbols."""
        if token.type == "EOF":
            return self.grammar.ENDMARKER
        if token.type == "IDENTIFIER":
            return "ID"
        if token.type == "NUMBER":
            return "NUM"
        if token.type == "STRING":
            return "STR"
        if token.type == "KEYWORD":
            return token.value
        if token.type == "SEPARATOR":
            return token.value
        if token.type == "OPERATOR":
            if token.value == "=":
                return "="
            if token.value in ["+", "-"]:
                return token.value
            if token.value in ["<", ">", "==", "!=", "<=", ">="]:
                return "RELOP"
        return "UNKNOWN"

    def _synchronize_nonterminal(self, nonterminal):
        """Panic-mode: skip tokens until FOLLOW(nonterminal) or EOF, then pop nonterminal."""
        sync_set = self.grammar.follow.get(nonterminal, set())
        lookahead = self._get_terminal_key(self.current_token)

        if lookahead in sync_set:
            return

        while self.current_token.type != "EOF":
            lookahead = self._get_terminal_key(self.current_token)
            if lookahead in sync_set:
                return
            self.current_token = self.scanner.get_next_token()

    def _record_error(self, message):
        self.errors.append(message)

    def parse(self):
        """Executes the table-driven parsing algorithm and returns the Parse Tree."""
        while self.stack:
            top_symbol, parent_node = self.stack.pop()

            if top_symbol == self.grammar.ENDMARKER:
                if self.current_token.type == "EOF":
                    break
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: Expected EOF, got {self.current_token.value}"
                    )
                    self.current_token = self.scanner.get_next_token()
                    continue

            # 1. Handle Terminals on top of the stack
            if top_symbol in self.grammar.terminals:
                if top_symbol == self.grammar.EPSILON:
                    parent_node.symbol = "ε"
                    continue

                terminal_key = self._get_terminal_key(self.current_token)
                if top_symbol == terminal_key:
                    parent_node.lexeme = self.current_token.value
                    self.current_token = self.scanner.get_next_token()
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: Expected '{top_symbol}', got '{self.current_token.value}'"
                    )
                    # Terminal mismatch recovery: discard one input symbol.
                    if self.current_token.type != "EOF":
                        self.current_token = self.scanner.get_next_token()

            # 2. Handle Non-Terminals on top of the stack (Consult Table M)
            else:
                terminal_key = self._get_terminal_key(self.current_token)
                production = self.grammar.parsing_table.get(top_symbol, {}).get(terminal_key)

                if production is not None:
                    # Create children nodes for the parse tree in forward order
                    child_nodes = [ParseTreeNode(sym) for sym in production]
                    parent_node.children.extend(child_nodes)

                    # Push children onto the stack in REVERSE order
                    for child in reversed(child_nodes):
                        self.stack.append((child.symbol, child))
                else:
                    self._record_error(
                        f"Line {self.current_token.line}: No rule for {top_symbol} with lookahead '{self.current_token.value}'"
                    )
                    self._synchronize_nonterminal(top_symbol)

        return self.root