#!/usr/bin/env python
"""Mini file dialog — intentionally lightweight.

Does NOT support preview_img, video_preview, or tool_tip.
Keeps a simple Treeview UI for speed and low memory.
"""
from __future__ import annotations

import os
from typing import List, Optional

import customtkinter as ctk
import tkinter as tk
from CTkMessagebox import CTkMessagebox
from _tkinter import TclError
from tkinter import ttk

from ..core.filesystem import prompt_create_folder
from ..resources.icons import load_mini_icons
from ..system.platform import System


class MiniDialog:
    """Compact file dialog (Mini style).

    Public attribute contract (used by ``_functions``):
        selected_path, selected_paths, selected_item, selected_items
    """

    def __init__(
        self,
        method: str,
        hidden: bool = False,
        filetypes: Optional[List[str]] = None,
        autocomplete: bool = False,
        initial_dir: str = ".",
        _extra_method: str = "",
        foldercreation: bool = True,
        geometry: str = "500x400",
        title: str = "CTkFileDialog",
    ):
        self.master = ctk.CTkToplevel()
        self.master.geometry(geometry_string=geometry)
        self.master.title(title)
        self._extra_method = _extra_method
        self.foldercreation = foldercreation
        self.tab_index = -1
        self.method = method
        self.hidden = hidden
        self.filetypes = filetypes
        self.autocomplete = autocomplete
        self.initial_dir = initial_dir

        if not self.initial_dir:
            self.initial_dir = os.getcwd()
        else:
            self.initial_dir = System.get_path(path=self.initial_dir)

        self.selected_path = ""
        self.selected_paths: list = []
        self.selected_items: list = []
        self.selected_item = ""
        self.files = {"name": [], "path": []}
        self.absolute_paths: list = []
        self.max_index = 0
        self.filtered_paths: list = []

        self.folder_image, self.file_image = load_mini_icons()

        self._build_top()
        self._build_center()
        self.list_files()
        self.master.bind_all("<Alt-Left>", lambda _: self._up())
        self.master.wait_visibility()
        self.master.grab_set()
        self.master.wait_window()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_path(self) -> str:
        return os.path.abspath(
            os.path.expandvars(os.path.expanduser(self.initial_dir))
        )

    def _create_new_folder(self) -> None:
        if not self.foldercreation:
            return
        prompt_create_folder(self.initial_dir, on_success=self.list_files)

    def update_entry(self, path) -> None:
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, path)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_top(self) -> None:
        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        self.path_frame = ctk.CTkFrame(self.frame)
        self.path_frame.pack(fill=ctk.X, padx=10, pady=10)

        self.path_entry = ctk.CTkEntry(self.path_frame)
        self.path_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT, padx=10, pady=10)
        self.path_entry.bind("<Return>", lambda _: self._on_enter_path())
        self.path_entry.insert(0, self._get_path())

        if self.autocomplete:
            for bind in ("<Tab>", "<Down>", "<Up>"):
                self.path_entry.bind(bind, self._autocomplete)

        ctk.CTkButton(
            self.path_frame, text="↑", width=30, command=self._up
        ).pack(side=ctk.RIGHT, padx=10, pady=10)

        if self.foldercreation:
            ctk.CTkButton(
                self.path_frame, text="＋", width=30, command=self._create_new_folder
            ).pack(side=ctk.RIGHT, padx=(0, 10), pady=10)

        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill=ctk.X, padx=10, pady=(0, 10))
        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(
            side=ctk.LEFT, padx=(0, 10)
        )
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Type to search files..."
        )
        self.search_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT)
        self.search_entry.bind("<KeyRelease>", lambda _: self._search_files())

        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="OK", command=self._on_select).pack(
            side=ctk.RIGHT
        )
        ctk.CTkButton(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side=ctk.RIGHT, padx=10
        )

    def _build_center(self) -> None:
        self.tree_frame = ctk.CTkFrame(self.frame)
        self.tree_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            style.configure(
                "Treeview",
                background="#242424",
                foreground="#FFFFFF",
                fieldbackground="#242424",
                bordercolor="#242424",
                rowheight=30,
            )
            style.map(
                "Treeview",
                background=[("selected", "#444444")],
                foreground=[("selected", "#FFFFFF")],
            )
        else:
            style.configure(
                "Treeview",
                background="#FFFFFF",
                foreground="#000000",
                fieldbackground="#FFFFFF",
                bordercolor="#DDDDDD",
                rowheight=30,
            )
            style.map(
                "Treeview",
                background=[("selected", "#E0E0E0")],
                foreground=[("selected", "#000000")],
            )

        multi = self.method in (
            "askopenfilenames",
            "askopenfiles",
            "askdirectories",
            "askopenpathnames",
        )
        self.tree = ttk.Treeview(
            self.tree_frame,
            show="tree",
            selectmode="extended" if multi else "browse",
        )
        self.tree.bind("<Double-1>", self._on_click)
        self.tree.bind("<Button-1>", self._on_select_item)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ------------------------------------------------------------------
    # Listing / search
    # ------------------------------------------------------------------

    def list_files(self) -> None:
        path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(self.path_entry.get()))
        )
        if os.path.isfile(path):
            return
        if not os.path.exists(path):
            return
        try:
            try:
                for item in self.tree.get_children():
                    self.tree.delete(item)
            except TclError:
                return

            self.files = {"name": [], "path": []}
            filtered = []

            for f in os.scandir(path):
                if (
                    (
                        f.is_dir()
                        or (
                            self.method not in ("askdirectory", "askdirectories")
                            and f.is_file()
                        )
                    )
                    and (self.hidden or not f.name.startswith("."))
                    and (
                        f.is_dir()
                        or not self.filetypes
                        or any(f.name.endswith(ext) for ext in self.filetypes)
                    )
                ):
                    filtered.append(f)
                    self.files["name"].append(f.name)
                    self.files["path"].append(f.path)

            sorted_files = sorted(
                filtered, key=lambda f: (not f.is_dir(), f.name.lower())
            )
            self.update_entry(path=path)

            for f in sorted_files:
                icon = self.folder_image if f.is_dir() else self.file_image
                self.tree.insert("", tk.END, text=f.name, image=icon)

            self.absolute_paths = [f.path for f in sorted_files]

        except PermissionError:
            CTkMessagebox(
                message="Permission Denied!", title="Error", icon="cancel"
            )
            self._on_cancel(destroy=False)
        else:
            self.max_index = len(self.files["name"])

    def _search_files(self) -> None:
        if not hasattr(self, "files") or not self.files["name"]:
            return
        query = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not query:
            self.list_files()
            return

        self.filtered_paths = []
        for name, path in zip(self.files["name"], self.files["path"]):
            if query in name.lower():
                is_dir = os.path.isdir(path)
                icon = self.folder_image if is_dir else self.file_image
                self.tree.insert("", tk.END, text=name, image=icon)
                self.filtered_paths.append(path)
        self.absolute_paths = self.filtered_paths

    # ------------------------------------------------------------------
    # Selection / navigation
    # ------------------------------------------------------------------

    def _autocomplete(self, event: tk.Event) -> str:
        if not self.files["name"] or not hasattr(self, "max_index"):
            return "break"
        if event.keysym == "Up":
            self.tab_index = (self.tab_index - 1) % self.max_index
        else:
            self.tab_index = (self.tab_index + 1) % self.max_index

        path = self.absolute_paths[self.tab_index]
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, path)
        item_id = self.tree.get_children()[self.tab_index]
        self.tree.focus(item_id)
        self.tree.selection_set(item_id)
        self.tree.see(item_id)
        self.selected_item = path
        return "break"

    def _on_enter_path(self) -> None:
        path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(self.path_entry.get()))
        )
        if os.path.isdir(path):
            self.initial_dir = path
            self.list_files()
        else:
            if os.path.isfile(path):
                return
            self.path_entry.configure(state="normal")
            if not os.path.exists(path=path):
                self._on_cancel(destroy=False)
                self.update_entry(path=self.initial_dir)
                CTkMessagebox(
                    title="Error",
                    icon="cancel",
                    message="No such file or directory!",
                )

    def _on_cancel(self, destroy: bool = True) -> None:
        self.selected_path = None
        self.selected_item = None
        self.selected_paths = None
        self.selected_items = None
        if destroy:
            self.master.destroy()

    def _on_select(self) -> None:
        path = self.path_entry.get().strip() if hasattr(self, "path_entry") else ""
        if path:
            path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
            if not os.path.dirname(path):
                path = os.path.join(self.initial_dir, path)

        if self.method in ("asksaveasfile", "asksaveasfilename"):
            if not path or os.path.isdir(path):
                return
            if os.path.exists(path) and self._extra_method != "askopenfile":
                opts = CTkMessagebox(
                    message="This file already exists! Do you want to overwrite it?",
                    title="Error",
                    icon="warning",
                    option_1="Yes",
                    option_2="No",
                )
                if opts.get() == "No":
                    return
            self.selected_path = path
            self.master.destroy()
            return

        if self.method in ("askopenfiles", "askopenfilenames"):
            selected_items = self.tree.selection()
            selected_paths = [
                self.absolute_paths[self.tree.index(item)]
                for item in selected_items
                if os.path.isfile(self.absolute_paths[self.tree.index(item)])
            ]
            if selected_paths:
                self.selected_paths = selected_paths
                self.master.destroy()
            return

        if self.method == "askdirectories":
            selected_items = self.tree.selection()
            selected_paths = [
                self.absolute_paths[self.tree.index(item)]
                for item in selected_items
                if os.path.isdir(self.absolute_paths[self.tree.index(item)])
            ]
            if selected_paths:
                self.selected_paths = selected_paths
                self.master.destroy()
            return

        if self.method == "askopenpathnames":
            selected_items = self.tree.selection()
            selected_paths = [
                self.absolute_paths[self.tree.index(item)] for item in selected_items
            ]
            if selected_paths:
                self.selected_paths = selected_paths
                self.master.destroy()
            return

        if self.method in (
            "askopenfilename",
            "askopenfile",
            "askdirectory",
            "askopenpathname",
        ):
            if not self.selected_item:
                return
            if self.method == "askdirectory" and os.path.isdir(self.selected_item):
                self.selected_path = self.selected_item
                self.master.destroy()
                return
            if self.method in ("askopenfilename", "askopenfile") and os.path.isfile(
                self.selected_item
            ):
                self.selected_path = self.selected_item
                self.master.destroy()
                return
            if self.method == "askopenpathname":
                self.selected_path = self.selected_item
                self.master.destroy()
                return

    def _on_select_item(self, event=None) -> None:
        selected_item = self.tree.focus()
        items = self.tree.get_children()
        if not selected_item or not items:
            return
        try:
            idx = items.index(selected_item)
            if idx < len(self.absolute_paths):
                self.selected_item = self.absolute_paths[idx]
        except (ValueError, IndexError):
            pass

    def _on_click(self, event=None) -> None:
        selected_item = self.tree.focus()
        items = self.tree.get_children()
        if not selected_item:
            return
        try:
            idx = items.index(selected_item)
            if idx >= len(self.absolute_paths):
                return
            self.selected_item = self.absolute_paths[idx]
        except (ValueError, IndexError):
            return

        if os.path.isdir(self.selected_item):
            self.initial_dir = self.selected_item
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, self.selected_item)
            self.list_files()
            return
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.selected_item)

    def _up(self) -> None:
        current_path = os.path.abspath(
            os.path.expandvars(os.path.expanduser(self.initial_dir))
        )
        self.initial_dir = os.path.dirname(current_path)
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.initial_dir)
        self.list_files()


# Backward-compatible alias
_MiniDialog = MiniDialog
