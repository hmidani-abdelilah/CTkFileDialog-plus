#!/usr/bin/env python
"""Backward-compatibility shim for platform helpers."""
from .system.platform import find_owner, System

__all__ = ["find_owner", "System"]
