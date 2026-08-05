#!/usr/bin/env python
"""Search / filter helpers."""
from __future__ import annotations

from typing import List


def filter_by_query(files: List[str], query: str) -> List[str]:
    """Case-insensitive substring filter on file names."""
    q = (query or "").lower().strip()
    if not q:
        return list(files)
    return [f for f in files if q in f.lower()]
