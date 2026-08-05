#!/usr/bin/env python
"""Icon loading for Default and Mini dialogs."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import customtkinter as ctk
from PIL import Image
import tkinter as tk

# Package root (CTkFileDialog/)
_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_ICON_DIR = _PACKAGE_DIR / "icons"
_MINI_ICON_DIR = _ICON_DIR / "_IconsMini"

# Extension → icon key mapping used by Default dialog
EXTENSION_ICONS: Dict[str, str] = {
    ".webp": "webp",
    ".awk": "bash",
    ".mp4": "video",
    ".mvk": "video",
    ".sh": "bash",
    ".zsh": "bash",
    ".py": "python",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".txt": "text",
    ".js": "javascript",
    ".md": "markdown",
    ".php": "php",
    ".html": "html",
    ".css": "css",
    ".ini": "ini",
    ".conf": "conf",
    ".json": "json",
    ".odt": "odt",
    ".pdf": "pdf",
    ".exe": "exe",
    ".gz": "gz",
}

# Filename (without path) → logical name for Default CTkImage icons
_DEFAULT_ICON_FILES = {
    "folder": "folder.png",
    "bash": "bash.png",
    "image": "image.png",
    "python": "python.png",
    "text": "text.png",
    "markdown": "markdown.png",
    "javascript": "javascript.png",
    "php": "php.png",
    "html": "html.png",
    "css": "css.png",
    "ini": "ini.png",
    "conf": "conf.png",
    "exe": "exe.png",
    "odt": "odt.png",
    "pdf": "pdf.png",
    "json": "json.png",
    "gz": "gz.png",
    "video": "video.png",
    "awk": "bash.png",
    "webp": "image.png",
    "default": "text.png",
}


def load_default_icons(size: tuple[int, int] = (40, 40)) -> Dict[str, ctk.CTkImage]:
    """Load all Default-dialog CTkImage icons."""
    icons: Dict[str, ctk.CTkImage] = {}
    for key, filename in _DEFAULT_ICON_FILES.items():
        path = _ICON_DIR / filename
        icons[key] = ctk.CTkImage(Image.open(path), size=size)
    return icons


def load_mini_icons() -> tuple[tk.PhotoImage, tk.PhotoImage]:
    """Return (folder_image, file_image) for Mini dialog Treeview."""
    folder = tk.PhotoImage(file=str(_MINI_ICON_DIR / "folder.png"))
    file_img = tk.PhotoImage(file=str(_MINI_ICON_DIR / "file.png"))
    return folder, file_img


def icon_for_extension(ext: str, icons: Dict[str, ctk.CTkImage]) -> ctk.CTkImage:
    """Resolve a CTkImage for a file extension."""
    key = EXTENSION_ICONS.get(ext.lower(), "default")
    return icons.get(key, icons["default"])
