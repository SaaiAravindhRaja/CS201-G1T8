"""Small text-processing helpers shared across search components."""

from __future__ import annotations

from typing import List


def find_substring_positions(text: str, pattern: str) -> List[int]:
    """Return start indices of ``pattern`` occurrences inside ``text``.

    Both arguments are expected to be pre-normalized (e.g. already lower-cased)
    by the caller so that helper stays agnostic about casing rules.
    """
    if not pattern:
        return []
    positions: List[int] = []
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


__all__ = ["find_substring_positions"]
