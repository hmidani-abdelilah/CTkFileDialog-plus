#!/usr/bin/env python
"""Custom tooltip that tolerates destroyed widgets."""
from __future__ import annotations

import time

import _tkinter
from CTkToolTip import CTkToolTip


class CustomToolTip(CTkToolTip):
    """CTkToolTip subclass that safely hides when the parent is gone."""

    def _show(self) -> None:
        if not self.widget.winfo_exists():
            self.hide()
            self.destroy()
            return

        if self.status == "inside" and time.time() - self.last_moved >= self.delay:
            self.status = "visible"
            try:
                self.deiconify()
            except _tkinter.TclError:
                pass
