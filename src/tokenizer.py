"""Tokenization utility shared by indexing and query evaluation."""

from __future__ import annotations

import re
from typing import List

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def tokenize(text: str) -> List[str]:
    """Return lowercase alphanumeric tokens extracted from ``text``."""
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]


__all__ = ["tokenize"]
