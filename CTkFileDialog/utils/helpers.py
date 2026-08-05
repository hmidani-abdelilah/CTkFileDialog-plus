#!/usr/bin/env python
"""Shared pure helpers (no UI, no FS side-effects beyond path math)."""
from __future__ import annotations

import os
from typing import List, Optional, Tuple, Union


def normalize_filetypes(
    filetypes: Optional[List[Union[str, Tuple[str, str]]]],
) -> Optional[List[str]]:
    """Convert tkinter-style filetypes list into simplified extensions.

    Accepts a list of strings or ``(label, pattern)`` tuples where pattern
    may contain space-separated globs.  ``"*"`` / ``"*.*"`` become ``""``
    (match-all).  Leading ``*`` characters are stripped so ``"*.py"``
    becomes ``".py"``.
    """
    if not filetypes:
        return None
    normalized: list[str] = []
    for entry in filetypes:
        if isinstance(entry, (tuple, list)) and len(entry) >= 2:
            patterns = str(entry[1]).split()
            for pat in patterns:
                pat = pat.strip()
                if pat in ("*", "*.*"):
                    normalized.append("")
                else:
                    normalized.append(pat.lstrip("*"))
        else:
            normalized.append(str(entry))
    return normalized


def apply_defaultext(path: Optional[str], defaultext: Optional[str]) -> Optional[str]:
    """Append *defaultext* to *path* if it has no extension yet."""
    if not path or not defaultext:
        return path
    _, ext = os.path.splitext(path)
    if ext:
        return path
    if not defaultext.startswith("."):
        defaultext = "." + defaultext
    return path + defaultext


def fix_name(name: str, max_len: int = 18) -> str:
    """Truncate a display name for grid buttons."""
    if len(name) > max_len:
        return name[: max_len - 3]
    return name


def format_size(size: int) -> str:
    """Human-readable file size."""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"
