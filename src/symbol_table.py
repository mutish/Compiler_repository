"""Placeholder symbol table module.

Currently minimal: provides a simple SymbolTable class to be expanded later.
"""

class SymbolTable:
    def __init__(self):
        self.table = {}

    def define(self, name, info):
        self.table[name] = info

    def lookup(self, name):
        return self.table.get(name)

    def __repr__(self):
        return f"SymbolTable({self.table})"
