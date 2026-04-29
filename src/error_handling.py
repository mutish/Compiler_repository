"""Error handling utilities for the parser.

Currently provides light-weight helpers for recording errors or synchronization.
"""
from typing import List


def record_error(errors: List[str], message: str):
    errors.append(message)
