#!/usr/bin/env python
"""Public dialog functions — API surface is unchanged."""
from __future__ import annotations

from typing import List, Literal, Optional, TextIO, Tuple, Union

from typeguard import typechecked

from .ui.default_dialog import _DrawApp
from .ui.mini_dialog import _MiniDialog
from .utils.helpers import apply_defaultext, normalize_filetypes


# Re-export helpers under historical private names for any external use
_normalize_filetypes = normalize_filetypes
_apply_defaultext = apply_defaultext


@typechecked
def askopenfilename(
    style: Literal["Mini", "Default"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> str | None:
    """
    Displays a file dialog for selecting a single file and returns the file path.
    """
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilename",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else None
    elif style == "Mini":
        app = _MiniDialog(
            method="askopenfilename",
            filetypes=normalized,
            initial_dir=initial_dir,
            autocomplete=autocomplete,
            hidden=hidden,
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return app.selected_path


@typechecked
def askdirectory(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    autocomplete: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> str | None:
    """Displays a directory selection dialog and returns the selected path."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            method="askdirectory",
            autocomplete=autocomplete,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else None
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            method="askdirectory",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            title=title,
            geometry=geometry[1],
        )
        return app.selected_path if app.selected_path else None


@typechecked
def askopendirname(
    style: Literal["Default", "Mini"] = "Default",
    hidden: bool = False,
    autocomplete: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> str:
    """Allow the user to choose a single directory."""
    if style == "Default":
        app = _DrawApp(
            current_path=initial_dir,
            hidden=hidden,
            method="askdirectory",
            autocomplete=autocomplete,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else ""
    elif style == "Mini":
        app = _MiniDialog(
            initial_dir=initial_dir,
            hidden=hidden,
            method="askdirectory",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            title=title,
            geometry=geometry[1],
        )
        return app.selected_path if app.selected_path else ""


@typechecked
def askopendirnames(
    style: Literal["Default", "Mini"] = "Default",
    hidden: bool = False,
    autocomplete: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> tuple[str, ...]:
    """Allow the user to choose multiple directories (Ctrl/Shift + click)."""
    if style == "Default":
        app = _DrawApp(
            current_path=initial_dir,
            hidden=hidden,
            method="askdirectories",
            autocomplete=autocomplete,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return tuple(app.selected_objects) if app.selected_objects else tuple()
    elif style == "Mini":
        app = _MiniDialog(
            initial_dir=initial_dir,
            hidden=hidden,
            method="askdirectories",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            title=title,
            geometry=geometry[1],
        )
        return tuple(app.selected_paths) if app.selected_paths else tuple()


@typechecked
def askopenpathname(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> str:
    """Allow the user to choose a single file or folder."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenpathname",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else ""
    elif style == "Mini":
        app = _MiniDialog(
            method="askopenpathname",
            filetypes=normalized,
            initial_dir=initial_dir,
            autocomplete=autocomplete,
            hidden=hidden,
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return app.selected_path if app.selected_path else ""


@typechecked
def askopenpathnames(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> tuple[str, ...]:
    """Allow the user to choose multiple files and folders (Ctrl/Shift + click)."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenpathnames",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return tuple(app.selected_objects) if app.selected_objects else tuple()
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            autocomplete=autocomplete,
            method="askopenpathnames",
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return tuple(app.selected_paths) if app.selected_paths else tuple()


@typechecked
def askopenfilenames(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> tuple[str, ...] | None:
    """Displays a file dialog for multiple file selection."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilenames",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return tuple(app.selected_objects) if app.selected_objects else None
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            method="askopenfilenames",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return tuple(app.selected_paths) if app.selected_paths else None


@typechecked
def asksaveasfilename(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    defaultext: Optional[str] = None,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> str | None:
    """Displays a save file dialog and returns the selected path."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="asksaveasfilename",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return apply_defaultext(app.selected_file, defaultext) if app.selected_file else None
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            method="asksaveasfilename",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return apply_defaultext(app.selected_path, defaultext) if app.selected_path else None


@typechecked
def asksaveasfile(
    style: Literal["Default", "Mini"] = "Default",
    mode: Literal["r", "rb", "r+", "rb+", "r+b", "w", "wb", "w+", "wb+", "a", "ab", "a+", "ab+", "x", "xb"] = "w",
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    defaultext: Optional[str] = None,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
) -> TextIO | None:
    """Displays a save dialog and returns an open file object."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="asksaveasfile",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        selected = apply_defaultext(app.selected_file, defaultext)
        return open(selected, mode=mode, **kwargs) if selected else None
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            method="asksaveasfile",
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        selected = apply_defaultext(app.selected_path, defaultext)
        return open(selected, mode=mode, **kwargs) if selected else None


@typechecked
def askopenfile(
    style: Literal["Mini", "Default"] = "Default",
    mode: Literal["r", "rb", "r+", "rb+", "r+b", "w", "wb", "w+", "wb+", "a", "ab", "a+", "ab+", "x", "xb"] = "r",
    hidden: bool = False,
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
) -> TextIO | None:
    """Displays an open file dialog and returns an open file object."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfile",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return open(app.selected_file, mode=mode, **kwargs) if app.selected_file else None
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            method="askopenfile",
            autocomplete=autocomplete,
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return open(app.selected_path, mode=mode, **kwargs) if app.selected_path else None


@typechecked
def askopenfiles(
    style: Literal["Default", "Mini"] = "Default",
    mode: Literal["r", "rb", "r+", "rb+", "r+b", "w", "wb", "w+", "wb+", "a", "ab", "a+", "ab+", "x", "xb"] = "r",
    hidden: bool = False,
    filetypes: Optional[List[Union[str, Tuple[str, str]]]] = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    foldercreation: bool = True,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
) -> tuple[TextIO, ...] | None:
    """Displays a multi-file open dialog and returns multiple open file objects."""
    normalized = normalize_filetypes(filetypes)
    if style == "Default":
        app = _DrawApp(
            filetypes=normalized,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilenames",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            foldercreation=foldercreation,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return (
            tuple(open(f, mode=mode, **kwargs) for f in app.selected_objects)
            if app.selected_objects
            else None
        )
    elif style == "Mini":
        app = _MiniDialog(
            filetypes=normalized,
            initial_dir=initial_dir,
            hidden=hidden,
            autocomplete=autocomplete,
            method="askopenfilenames",
            foldercreation=foldercreation,
            geometry=geometry[1],
            title=title,
        )
        return (
            tuple(open(f, mode=mode, **kwargs) for f in app.selected_paths)
            if app.selected_paths
            else None
        )
