#!/usr/bin/env python
"""File sorting helpers."""
from __future__ import annotations

import os
from typing import List


def sort_files(files: List[str], current_path: str, sort_by: str = "name") -> List[str]:
    """Sort *files* (names relative to *current_path*).

    Directories always sort before files.  *sort_by* may be one of
    ``name``, ``date``, ``type``, ``size``, ``modified``.
    """

    def info(filename: str) -> dict:
        full = os.path.join(current_path, filename)
        try:
            st = os.stat(full)
            return {
                "name": filename.lower(),
                "date": st.st_mtime,
                "modified": st.st_mtime,
                "type": os.path.splitext(filename)[1].lower(),
                "size": st.st_size,
                "is_dir": os.path.isdir(full),
            }
        except OSError:
            return {
                "name": filename.lower(),
                "date": 0,
                "modified": 0,
                "type": "",
                "size": 0,
                "is_dir": os.path.isdir(full),
            }

    return sorted(
        files,
        key=lambda f: (not info(f)["is_dir"], info(f).get(sort_by, 0)),
    )
