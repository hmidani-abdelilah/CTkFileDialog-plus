#!/usr/bin/env python
"""Filesystem operations used by the dialogs."""
from __future__ import annotations

import os
import time
from typing import Any, Callable, List, Optional

from CTkMessagebox import CTkMessagebox

from ..system.platform import find_owner


def list_directory(
    path: str,
    *,
    method: str,
    hidden: bool = False,
    filetypes: Optional[List[str]] = None,
) -> List[str]:
    """Return names of entries in *path* filtered by dialog mode and options.

    Directories are always included (unless hidden).  Files are included
    unless the method is a pure directory-picker, and must match *filetypes*
    when provided.
    """
    dir_only = method in ("askdirectory", "askdirectories")
    result: List[str] = []
    try:
        for entry in os.scandir(path):
            if entry.name.startswith(".") and not hidden:
                continue
            if entry.is_dir():
                result.append(entry.name)
            elif not dir_only and entry.is_file():
                if not filetypes or any(entry.name.endswith(ext) for ext in filetypes):
                    result.append(entry.name)
    except (PermissionError, FileNotFoundError, OSError):
        raise
    return result


def create_folder(parent: str, name: str) -> Optional[str]:
    """Create a new folder under *parent*.

    Returns the new path on success, or ``None`` on failure (after showing
    a message box).  Raises nothing — errors are reported via UI.
    """
    name = (name or "").strip()
    if not name:
        return None
    new_path = os.path.join(parent, name)
    try:
        os.makedirs(new_path, exist_ok=False)
        return new_path
    except FileExistsError:
        CTkMessagebox(
            message="A file or folder with that name already exists!",
            title="Error",
            icon="cancel",
        )
    except PermissionError:
        CTkMessagebox(message="Permission denied!", title="Error", icon="cancel")
    except OSError as e:
        CTkMessagebox(
            message=f"Could not create folder: {e}",
            title="Error",
            icon="cancel",
        )
    return None


def get_file_info(path: str) -> str:
    """Return a multi-line tooltip string for *path*."""
    try:
        st = os.stat(path)
        owner = find_owner(path)
        fecha = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_ctime))
        return (
            f"File: {os.path.basename(path)}\n"
            f"    creation: {fecha}\n"
            f"    owner: {owner}\n"
            f"    path: {path}\n"
            f"                    "
        )
    except Exception as e:
        return f"Error getting info: {e}"


def prompt_create_folder(parent_path: str, on_success: Optional[Callable[[], Any]] = None) -> None:
    """Show an input dialog, create the folder, then call *on_success*."""
    import customtkinter as ctk

    dialog = ctk.CTkInputDialog(text="Enter new folder name:", title="New Folder")
    name = dialog.get_input()
    if create_folder(parent_path, name or "") and on_success:
        on_success()
