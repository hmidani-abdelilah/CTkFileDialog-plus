#!/usr/bin/env python
"""Platform-specific utilities (owner lookup, path helpers)."""
from __future__ import annotations

import os
import platform
from pathlib import Path


def find_owner(path) -> str:
    """Return the owner of *path* (Unix or Windows)."""
    system = platform.system()
    path = str(path)

    if system == "Windows":
        return _get_windows_owner(path)
    return _get_unix_owner(path)


def _get_unix_owner(path: str) -> str:
    try:
        return Path(path).owner()
    except Exception:
        return "unknown:unknown"


def _get_windows_owner(path: str) -> str:
    import ctypes
    from ctypes import wintypes

    GetNamedSecurityInfoW = ctypes.windll.advapi32.GetNamedSecurityInfoW
    LookupAccountSidW = ctypes.windll.advapi32.LookupAccountSidW
    LocalFree = ctypes.windll.kernel32.LocalFree

    OWNER_SECURITY_INFORMATION = 0x00000001
    SE_FILE_OBJECT = 1

    pSidOwner = ctypes.c_void_p()
    pSD = ctypes.c_void_p()

    result = GetNamedSecurityInfoW(
        ctypes.c_wchar_p(path),
        SE_FILE_OBJECT,
        OWNER_SECURITY_INFORMATION,
        ctypes.byref(pSidOwner),
        None, None, None,
        ctypes.byref(pSD),
    )

    if result != 0:
        return "unknown"

    name = ctypes.create_unicode_buffer(256)
    domain = ctypes.create_unicode_buffer(256)
    name_size = wintypes.DWORD(len(name))
    domain_size = wintypes.DWORD(len(domain))
    sid_name_use = wintypes.DWORD()

    success = LookupAccountSidW(
        None,
        pSidOwner,
        name,
        ctypes.byref(name_size),
        domain,
        ctypes.byref(domain_size),
        ctypes.byref(sid_name_use),
    )

    LocalFree(pSD)

    if not success:
        return "unknown"

    return f"{name.value}"


class System:
    """Thin path helpers used by both Default and Mini dialogs."""

    @staticmethod
    def get_path(path=None) -> str:
        if path is None:
            path = os.getcwd()
        return f"{path}" if path == os.getenv("HOME") else path

    @staticmethod
    def parse_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
