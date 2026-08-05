#!/usr/bin/env python
"""Backward-compatibility shim.

Historically all dialog classes lived in this module.  They have been
moved to ``CTkFileDialog.ui``.  This file re-exports the public names so
any external ``from CTkFileDialog.Dialog import _DrawApp`` continues to
work.
"""
from .ui.default_dialog import DrawApp, _DrawApp
from .ui.mini_dialog import MiniDialog, _MiniDialog
from .ui.tooltip import CustomToolTip
from .system.platform import System as _System

# Historical private name
_CustomToolTip = CustomToolTip

__all__ = [
    "DrawApp",
    "_DrawApp",
    "MiniDialog",
    "_MiniDialog",
    "CustomToolTip",
    "_CustomToolTip",
    "_System",
]
