"""Production rule utilities."""
from dataclasses import dataclass
from typing import List


@dataclass
class Production:
    lhs: str
    rhs: List[str]

    def __repr__(self):
        return f"{self.lhs} -> {' '.join(self.rhs)}"
