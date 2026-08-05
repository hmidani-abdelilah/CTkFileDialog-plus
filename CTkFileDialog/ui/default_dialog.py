#!/usr/bin/env python
"""Default (full) file dialog — advanced explorer UI.

Business logic (listing, sorting, search, media) lives in core/ and preview/.
This module only builds widgets and wires events.
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any, List, Optional

import _tkinter
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

from ..core.filesystem import get_file_info, list_directory, prompt_create_folder
from ..core.search import filter_by_query
from ..core.sorting import sort_files
from ..preview.media import get_video_frame, is_image, is_video, thumbnail_image
from ..resources.icons import icon_for_extension, load_default_icons
from ..system.platform import System
from ..utils.helpers import fix_name
from .tooltip import CustomToolTip

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BATCH_SIZE = 50
GRID_COLUMNS = 5
ICON_THUMB_SIZE = (32, 32)
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 60


class DrawApp:
    """Full-featured file dialog (Default style).

    Public attribute contract (used by ``_functions``):
        selected_file : str
        selected_objects : list
        app : CTkToplevel
    """

    def __init__(
        self,
        method: str,
        filetypes: Optional[List[str]] = None,
        bufering: int = 1,
        encoding: str = "utf-8",
        current_path: str = ".",
        hidden: bool = False,
        preview_img: bool = False,
        autocomplete: bool = False,
        video_preview: bool = False,
        tool_tip: bool = False,
        foldercreation: bool = True,
        title: str = "CTkFileDialog",
        geometry: str = "1320x720",
    ) -> None:
        self.foldercreation = foldercreation
        self.current_path = current_path
        if not self.current_path:
            self.current_path = os.getcwd()
        else:
            self.current_path = System.parse_path(path=self.current_path)

        self.autocomplete = autocomplete
        self.preview_img = preview_img
        self.bufering = bufering
        self.encoding = encoding
        self.hidden = hidden
        self.video_preview = video_preview
        self.suggest: list = []
        self.tool_tip = tool_tip
        self._all_buttons: list = []
        self._icon_cache: dict[str, ctk.CTkImage] = {}
        self.filetypes = filetypes
        self.tab_index = -1
        self.method = method
        self.current_theme = ctk.get_appearance_mode()
        self.view_mode = "grid"
        self.display_files: list = []
        self.BATCH = BATCH_SIZE
        self.selected_file = ""
        self.selected_objects: list = []
        self._temp_item = None
        self._temp_items: list = []
        self._selected_row_frames: list = []
        self.LOADED = 0
        self.files: list = []
        self.entire_paths: list | None = None

        self.icons = load_default_icons()

        self.app = ctk.CTkToplevel()
        self.app.title(string=title)
        self.app.geometry(geometry)
        self.app.protocol("WM_DELETE_WINDOW", self.protocol_windows)

        self._build_top_bar()
        self._build_left_side()
        self._build_center()
        try:
            self.app.grab_set()
        except _tkinter.TclError:
            pass

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def protocol_windows(self) -> None:
        try:
            self.app.destroy()
            self.app.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def close_app(self) -> None:
        if self.method in ("asksaveasfilename", "asksaveasfile"):
            if not os.path.isdir(self.PathEntry.get()):
                self.selected_file = self.PathEntry.get()
                self.protocol_windows()
                self.app.destroy()
                return

        if self._temp_item:
            self.protocol_windows()
            self.app.destroy()
            if self.method == "asksaveasfile":
                self.selected_file = self._temp_item
                return
            if self.method == "askopenfile":
                self.selected_file = self._temp_item
            else:
                self.selected_file = self._temp_item
                return

        if len(self._temp_items) >= 1:
            self.protocol_windows()
            self.app.destroy()
            if self.method in ("askopenfilenames", "askopenfiles"):
                seen: set = set()
                self.selected_objects = [
                    f
                    for f in self._temp_items
                    if not os.path.isdir(f) and f not in seen and not seen.add(f)
                ]
                return
            if self.method == "askdirectories":
                seen = set()
                self.selected_objects = [
                    f
                    for f in self._temp_items
                    if os.path.isdir(f) and f not in seen and not seen.add(f)
                ]
                return
            if self.method == "askopenpathnames":
                seen = set()
                self.selected_objects = [
                    f for f in self._temp_items if f not in seen and not seen.add(f)
                ]
                return

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def update_entry(self, path) -> None:
        self.PathEntry.configure(state="normal")
        self.PathEntry.delete(0, "end")
        self.PathEntry.insert(0, path)

    def btn_back(self, master: ctk.CTkToplevel) -> None:
        if self.current_path != os.path.dirname(self.current_path):
            self.current_path = os.path.dirname(self.current_path)
            self.update_entry(path=self.current_path)
            self._list_files(master)

    def navigate_to(self, path: str, master) -> None:
        try:
            path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

            if os.path.isdir(path):
                if self.method in ("askdirectory", "askopenpathname"):
                    self._temp_item = path
                self.current_path = Path(path)
                self.update_entry(path=self.current_path)
                self._list_files(master)
                return

            if self.method in ("asksaveasfile", "asksaveasfilename"):
                if os.path.isfile(path):
                    msg = CTkMessagebox(
                        message="This file exists. Do you want to overwrite it?",
                        icon="warning",
                        title="Warning",
                        option_1="Yes",
                        option_2="No",
                    )
                    if msg.get() == "No":
                        return
                self._temp_item = path
                self.close_app()
                return

            if self.method == "askopenfile":
                if not os.path.isfile(path):
                    CTkMessagebox(
                        message="File not found!", title="Error", icon="cancel"
                    )
                    self.PathEntry.delete(0, ctk.END)
                    self.PathEntry.insert(0, self.current_path)
                    return
                self._temp_item = path
                self.update_entry(self._temp_item)
                return

            if os.path.isfile(path):
                self._temp_item = path
                self.update_entry(self._temp_item)
                return

            self.PathEntry.delete(0, "end")
            self.PathEntry.insert(0, str(self.current_path))
            self.PathEntry.configure(state="normal")
            CTkMessagebox(
                message="No such file or directory!", title="Error", icon="cancel"
            )
        except PermissionError:
            CTkMessagebox(message="Permission denied!", title="Error", icon="cancel")
        except FileNotFoundError:
            CTkMessagebox(message="File Not Found!", title="Error", icon="cancel")

    def _create_new_folder(self) -> None:
        if not self.foldercreation:
            return
        prompt_create_folder(
            str(self.current_path),
            on_success=lambda: self._list_files(master=self.app),
        )

    # ------------------------------------------------------------------
    # Autocomplete
    # ------------------------------------------------------------------

    def _autocomplete(self, event) -> str:
        if not hasattr(self, "entire_paths") or not self.entire_paths:
            return "break"
        if not self.files:
            return "break"

        max_index = len(self.files)
        if event.keysym == "Up":
            self.tab_index = (self.tab_index - 1) % max_index
        else:
            self.tab_index = (self.tab_index + 1) % max_index

        path = self.entire_paths[self.tab_index]
        self.PathEntry.delete(0, ctk.END)
        self.PathEntry.insert(0, path)
        self._temp_item = path
        return "break"

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_top_bar(self) -> None:
        master = self.app
        top = ctk.CTkFrame(master=master, height=40, fg_color="transparent")
        top.pack(side="top", fill="x")

        def btn_exit():
            msg = CTkMessagebox(
                message="Do you want to exit?",
                title="Exit",
                option_1="Yes",
                option_2="No",
                icon="warning",
            )
            if msg.get() == "Yes":
                self.protocol_windows()
                self.selected_file = None
                self.selected_objects = []
                self._temp_item = None
                self._temp_items = []
                master.destroy()

        ctk.CTkButton(
            master=top,
            text="Exit",
            font=("Hack Nerd Font", 15),
            width=70,
            command=btn_exit,
            hover_color="red",
        ).pack(side="left", fill="x")

        self.PathEntry = ctk.CTkEntry(
            master=top, width=1070, corner_radius=0, insertwidth=0
        )
        self.PathEntry.insert(index=0, string=System.get_path(str(self.current_path)))
        self.PathEntry.pack(side="right", fill="y", padx=10, pady=10)
        self.PathEntry.bind(
            "<Return>",
            lambda e: self.navigate_to(
                path=self.PathEntry.get(), master=master
            ),
        )
        self.PathEntry.bind("<Alt-Left>", lambda e: self.btn_back(master=master))

        ctk.CTkButton(
            master=top,
            text="",
            font=("Hack Nerd Font", 15),
            width=70,
            command=lambda: self.btn_back(master=master),
        ).pack(side="left", fill="x", padx=10, pady=10)

        ctk.CTkButton(
            master=top,
            text="Ok",
            font=("Hack Nerd Font", 15),
            width=70,
            command=lambda: self.close_app(),
        ).pack(side="left", fill="x", padx=10, pady=10)

        if self.foldercreation:
            ctk.CTkButton(
                master=top,
                text="New Folder",
                font=("Hack Nerd Font", 15),
                width=100,
                command=self._create_new_folder,
            ).pack(side="left", fill="x", padx=10, pady=10)

        if self.autocomplete:
            for key in ("<Down>", "<Up>", "<Tab>"):
                self.PathEntry.bind(key, self._autocomplete)

        self.app.bind_all("<Alt-Left>", lambda e: self.btn_back(master=self.app))

        # Search + view + sort bar
        search_frame = ctk.CTkFrame(master=master, fg_color="transparent", height=40)
        search_frame.pack(side="top", fill="x", padx=10, pady=(5, 10))
        self.SearchFrame = search_frame

        ctk.CTkLabel(search_frame, text="Search:", font=("Arial", 12)).pack(
            side="left", padx=(0, 10)
        )
        self.SearchEntry = ctk.CTkEntry(
            search_frame, placeholder_text="Type to search files..."
        )
        self.SearchEntry.pack(expand=True, fill="x", side="left", padx=(0, 20))
        self.SearchEntry.bind("<KeyRelease>", lambda _: self._search_files())

        ctk.CTkLabel(search_frame, text="View:", font=("Arial", 12)).pack(
            side="left", padx=(0, 10)
        )
        self.grid_btn = ctk.CTkButton(
            search_frame,
            text="📊 Grid",
            width=60,
            command=lambda: self._set_view_mode("grid"),
        )
        self.grid_btn.pack(side="left", padx=5)
        self.list_btn = ctk.CTkButton(
            search_frame,
            text="📋 List",
            width=60,
            command=lambda: self._set_view_mode("list"),
        )
        self.list_btn.pack(side="left", padx=5)

        ctk.CTkLabel(search_frame, text="Sort:", font=("Arial", 12)).pack(
            side="left", padx=(20, 10)
        )
        self.sort_var = ctk.StringVar(value="name")
        self.sort_menu = ctk.CTkOptionMenu(
            search_frame,
            values=["name", "date", "type", "size", "modified"],
            command=self._on_sort_change,
            variable=self.sort_var,
        )
        self.sort_menu.pack(side="left", padx=5)

    def _build_left_side(self) -> None:
        master = self.app
        left = ctk.CTkFrame(master=master, width=200)
        left.pack(side="left", fill="y", padx=10, pady=10)
        left.pack_propagate(False)

        home = os.path.expanduser("~")
        folders = {f"{str(os.getenv('HOME')).replace('/home/', '')}": home}

        dir_file = os.path.join(home, ".config/user-dirs.dirs")
        pattern = re.compile(r'XDG_\w+_DIR="(.+?)"')

        import platform

        if platform.system() == "Linux":
            if not os.path.exists(path=dir_file):
                raise FileNotFoundError(
                    f"The file {dir_file} is required for the program to run!"
                )
            with open(dir_file, "r") as f:
                for line in f:
                    if not line.startswith("#") and line.strip():
                        match = pattern.search(line)
                        if match:
                            path = os.path.expandvars(match.group(1))
                            name = os.path.basename(os.path.normpath(path))
                            if name != f"{os.getenv('USER')}":
                                folders[name] = path
        elif platform.system() == "Windows":
            home_p = Path.home()
            win_folders = {
                home_p.name: str(home_p),
                "Desktop": home_p / "Desktop",
                "Documents": home_p / "Documents",
                "Downloads": home_p / "Downloads",
                "Pictures": home_p / "Pictures",
                "Music": home_p / "Music",
                "Videos": home_p / "Videos",
            }
            folders = {k: v for k, v in win_folders.items()}

        ctk.CTkLabel(
            master=left, text="Places", font=("Hack Nerd Font", 15)
        ).pack(side=ctk.TOP, padx=5, pady=5)

        icons_map = {
            os.getenv("USER"): "",
            "Desktop": "",
            "Downloads": "",
            "Documents": "",
            "Pictures": "",
            "Music": "",
            "Videos": "",
            "Templates": "",
            "Public": "",
        }

        for name, path in folders.items():
            icon = icons_map.get(name, "")
            ctk.CTkButton(
                master=left,
                text=f"    {icon}  {name}",
                font=("Hack Nerd Font", 14),
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color=(
                    "#000000"
                    if self.current_theme.lower() == "light"
                    else "#cccccc"
                ),
                corner_radius=2,
                border_width=0,
                command=lambda r=path: self.navigate_to(path=r, master=master),
            ).pack(fill="x", pady=4)

    def _build_center(self) -> None:
        master = self.app
        self.CenterSideFrame = ctk.CTkScrollableFrame(master=master)
        self.CenterSideFrame.pack(
            expand=True, side="top", fill="both", padx=10, pady=10
        )
        self._bind_scroll()
        self.content_frame = ctk.CTkFrame(master=self.CenterSideFrame)
        self.content_frame.pack(
            side="top", fill="both", expand=True, padx=20, pady=10
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self._list_files(master=master)

    def _bind_scroll(self) -> None:
        canvas = self.CenterSideFrame._parent_canvas

        def _on_mousewheel(event):
            try:
                x_root = getattr(event, "x_root", None)
                y_root = getattr(event, "y_root", None)
                if x_root is not None and y_root is not None:
                    x1 = self.CenterSideFrame.winfo_rootx()
                    y1 = self.CenterSideFrame.winfo_rooty()
                    x2 = x1 + self.CenterSideFrame.winfo_width()
                    y2 = y1 + self.CenterSideFrame.winfo_height()
                    if not (x1 <= x_root <= x2 and y1 <= y_root <= y2):
                        return

                if hasattr(event, "num"):
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                        self._check_scroll(self.app)
                        return "break"
                    if event.num == 5:
                        canvas.yview_scroll(1, "units")
                        self._check_scroll(self.app)
                        return "break"
                if hasattr(event, "delta"):
                    canvas.yview_scroll(-int(event.delta / 120), "units")
                    self._check_scroll(self.app)
                    return "break"
            except Exception:
                pass

        self.app.bind_all("<MouseWheel>", _on_mousewheel)
        self.app.bind_all("<Button-4>", _on_mousewheel)
        self.app.bind_all("<Button-5>", _on_mousewheel)
        for widget in canvas.winfo_children():
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)

    # ------------------------------------------------------------------
    # File listing / display
    # ------------------------------------------------------------------

    def __clear__(self) -> None:
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except (_tkinter.TclError, Exception):
                pass
        self._selected_row_frames.clear()
        self._icon_cache.clear()

    def _list_files(self, master: ctk.CTkToplevel) -> None:
        self.LOADED = 0
        self.BATCH = BATCH_SIZE
        self.selected_objects.clear()
        self._all_buttons.clear()
        self.CenterSideFrame._parent_canvas.yview_moveto(0)
        self.__clear__()

        path = self.current_path
        try:
            self.files = list_directory(
                str(path),
                method=self.method,
                hidden=self.hidden,
                filetypes=self.filetypes,
            )
        except (PermissionError, FileNotFoundError, OSError):
            self.files = []
            self.display_files = []
            return

        if not self.files:
            self.display_files = []
            return

        if self.autocomplete:
            self.entire_paths = [
                os.path.join(self.current_path, f) for f in self.files
            ] or None

        sorted_files = sort_files(
            self.files, str(self.current_path), self.sort_var.get()
        )
        self._display_files(sorted_files)

    def _display_files(self, files: list) -> None:
        self.display_files = files
        self.LOADED = 0
        total = len(files)
        if total <= 0:
            return
        if self.view_mode == "grid":
            self._load_grid_files(total)
        else:
            self._load_list_files(total)

    def _resolve_icon(self, full_path: str, filename: str):
        cached = self._icon_cache.get(full_path)
        if cached is not None:
            return cached

        if os.path.isdir(full_path):
            icon = self.icons["folder"]
            self._icon_cache[full_path] = icon
            return icon

        if self.preview_img and is_image(full_path):
            img = thumbnail_image(full_path, ICON_THUMB_SIZE)
            if img is not None:
                icon = ctk.CTkImage(
                    light_image=img, dark_image=img, size=ICON_THUMB_SIZE
                )
                self._icon_cache[full_path] = icon
                return icon
            icon = self.icons.get("image", self.icons["default"])
            self._icon_cache[full_path] = icon
            return icon

        if self.video_preview and is_video(full_path):
            frame = get_video_frame(full_path, frame_number=10)
            if frame is not None:
                frame.thumbnail(ICON_THUMB_SIZE)
                icon = ctk.CTkImage(
                    light_image=frame, dark_image=frame, size=ICON_THUMB_SIZE
                )
                self._icon_cache[full_path] = icon
                return icon
            icon = self.icons.get("video", self.icons["default"])
            self._icon_cache[full_path] = icon
            return icon

        ext = os.path.splitext(filename)[1].lower()
        icon = icon_for_extension(ext, self.icons)
        self._icon_cache[full_path] = icon
        return icon

    def _text_color(self) -> str:
        return (
            "#000000" if self.current_theme.lower() == "light" else "#cccccc"
        )

    def _make_grid_button(
        self,
        full_path: str,
        filename: str,
        file_type: str,
        size_str: str,
        master,
    ):
        icon = self._resolve_icon(full_path, filename)
        fixed_name = fix_name(name=filename)
        command = None
        if self.method not in (
            "askopenfilenames",
            "askdirectories",
            "askopenpathnames",
        ):
            command = lambda r=full_path: self.navigate_to(path=r, master=master)

        button_text = f"{fixed_name}\n{file_type} • {size_str}"
        boton = ctk.CTkButton(
            master=self.content_frame,
            text=button_text,
            image=icon,
            compound="top",
            width=BUTTON_WIDTH,
            height=100,
            anchor="center",
            fg_color="transparent",
            hover_color="#8da3ae",
            text_color=self._text_color(),
            command=command,
        )
        if self.tool_tip:
            CustomToolTip(widget=boton, message=get_file_info(full_path))
        if self.method in (
            "askopenfilenames",
            "askopenfiles",
            "askdirectories",
            "askopenpathnames",
        ):
            boton.bind(
                "<Button-1>",
                lambda event, r=full_path, b=boton: self._handle_click(
                    event, r, master, b
                ),
            )
        return boton

    def _load_grid_files(self, cantidad: int) -> None:
        while self.LOADED < len(self.display_files) and cantidad > 0:
            file = self.display_files[self.LOADED]
            full_path = os.path.join(self.current_path, file)
            if self.method in ("askdirectory", "askdirectories") and os.path.isfile(
                full_path
            ):
                self.LOADED += 1
                continue

            try:
                st = os.stat(full_path)
                file_size = st.st_size
            except OSError:
                file_size = 0

            is_dir = os.path.isdir(full_path)
            file_type = (
                "Directory"
                if is_dir
                else os.path.splitext(file)[1][1:].upper() or "File"
            )

            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            row = self.LOADED // GRID_COLUMNS
            col = self.LOADED % GRID_COLUMNS
            boton = self._make_grid_button(
                full_path,
                file,
                file_type,
                size_str,
                self.app,
            )
            boton.grid(row=row, column=col, padx=10, pady=10)
            self.LOADED += 1
            cantidad -= 1

        try:
            self.content_frame.update_idletasks()
            self.CenterSideFrame._parent_canvas.configure(
                scrollregion=self.CenterSideFrame._parent_canvas.bbox("all")
            )
        except Exception:
            pass

    def _load_list_files(self, cantidad: int) -> None:
        if self.LOADED == 0:
            header_bg = "#343638" if self.current_theme.lower() == "dark" else "#f0f0f0"
            header_fg = "#ffffff" if self.current_theme.lower() == "dark" else "#000000"
            header_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color=header_bg,
                corner_radius=10,
                height=40,
            )
            header_frame.pack(fill="x", padx=10, pady=(0, 8))
            header_frame.grid_columnconfigure(0, minsize=56)
            header_frame.grid_columnconfigure(1, weight=1)
            header_frame.grid_columnconfigure(2, minsize=80)
            header_frame.grid_columnconfigure(3, minsize=80)
            header_frame.grid_columnconfigure(4, minsize=120)
            header_frame.grid_rowconfigure(0, minsize=40)

            ctk.CTkLabel(
                master=header_frame,
                text="",
                width=56,
                anchor="w",
                text_color=header_fg,
                font=("Arial", 11, "bold"),
            ).grid(row=0, column=0, padx=12, pady=8, sticky="w")
            ctk.CTkLabel(
                master=header_frame,
                text="Name",
                anchor="w",
                text_color=header_fg,
                font=("Arial", 11, "bold"),
            ).grid(row=0, column=1, padx=4, pady=8, sticky="ew")
            ctk.CTkLabel(
                master=header_frame,
                text="Type",
                anchor="w",
                text_color=header_fg,
                font=("Arial", 11, "bold"),
            ).grid(row=0, column=2, padx=4, pady=8, sticky="w")
            ctk.CTkLabel(
                master=header_frame,
                text="Size",
                anchor="w",
                text_color=header_fg,
                font=("Arial", 11, "bold"),
            ).grid(row=0, column=3, padx=4, pady=8, sticky="w")
            ctk.CTkLabel(
                master=header_frame,
                text="Modified",
                anchor="w",
                text_color=header_fg,
                font=("Arial", 11, "bold"),
            ).grid(row=0, column=4, padx=4, pady=8, sticky="e")

        while self.LOADED < len(self.display_files) and cantidad > 0:
            file = self.display_files[self.LOADED]
            full_path = os.path.join(self.current_path, file)
            if self.method in ("askdirectory", "askdirectories") and os.path.isfile(
                full_path
            ):
                self.LOADED += 1
                continue

            try:
                st = os.stat(full_path)
                file_size = st.st_size
                mod_time = time.strftime(
                    "%Y-%m-%d %H:%M", time.localtime(st.st_mtime)
                )
            except OSError:
                file_size = 0
                mod_time = "N/A"

            is_dir = os.path.isdir(full_path)
            file_type = (
                "Directory"
                if is_dir
                else os.path.splitext(file)[1][1:].upper() or "File"
            )
            icon = self._resolve_icon(full_path, file)

            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            row_bg = "#2f3136" if self.current_theme.lower() == "dark" else "#f7f7f7"
            item_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color=row_bg,
                corner_radius=12,
            )
            item_frame.pack(fill="x", padx=10, pady=4, ipady=8)

            ctk.CTkLabel(
                master=item_frame,
                image=icon,
                text="",
                width=56,
                anchor="w",
            ).pack(side="left", padx=(12, 4), pady=8)

            ctk.CTkLabel(
                master=item_frame,
                text=file,
                anchor="w",
                text_color=self._text_color(),
                font=("Arial", 11, "bold"),
            ).pack(side="left", fill="x", expand=True, padx=4, pady=8)

            ctk.CTkLabel(
                master=item_frame,
                text=file_type,
                anchor="w",
                text_color="#a6a6a6" if self.current_theme.lower() == "dark" else "#606060",
                font=("Arial", 10),
                width=80,
            ).pack(side="left", padx=4, pady=8)

            ctk.CTkLabel(
                master=item_frame,
                text=size_str,
                anchor="w",
                text_color="#a6a6a6" if self.current_theme.lower() == "dark" else "#606060",
                font=("Arial", 10),
                width=80,
            ).pack(side="left", padx=4, pady=8)

            date_label = ctk.CTkLabel(
                master=item_frame,
                text=mod_time,
                anchor="e",
                text_color=self._text_color(),
                font=("Arial", 10),
                width=120,
            )
            date_label.pack(side="left", padx=(4, 12), pady=8)

            command = None
            if self.method not in (
                "askopenfilenames",
                "askdirectories",
                "askopenpathnames",
            ):
                command = lambda r=full_path: self.navigate_to(
                    path=r, master=self.app
                )

            if self.method in (
                "askopenfilenames",
                "askopenfiles",
                "askdirectories",
                "askopenpathnames",
            ):
                self._selected_row_frames.append(item_frame)
                def row_callback(event, r=full_path, f=item_frame):
                    self._select_list_row(event, r, f)
            elif command is not None:
                def row_callback(event, r=full_path):
                    command(r)
            else:
                row_callback = None

            if row_callback is not None:
                item_frame.bind("<Button-1>", row_callback)
                for child in item_frame.winfo_children():
                    child.bind("<Button-1>", row_callback)

            self.LOADED += 1
            cantidad -= 1

        try:
            self.content_frame.update_idletasks()
            self.CenterSideFrame._parent_canvas.configure(
                scrollregion=self.CenterSideFrame._parent_canvas.bbox("all")
            )
        except Exception:
            pass

    def _check_scroll(self, master) -> None:
        try:
            canvas = self.CenterSideFrame._parent_canvas
            yview = canvas.yview()
            if not hasattr(self, "display_files") or not self.display_files:
                return
            if yview[1] > 0.80 and self.LOADED < len(self.display_files):
                if self.view_mode == "grid":
                    self._load_grid_files(self.BATCH)
                else:
                    self._load_list_files(self.BATCH)
        except _tkinter.TclError:
            pass

    def _search_files(self) -> None:
        if not hasattr(self, "files") or not self.files:
            return
        query = self.SearchEntry.get()
        self.__clear__()
        if not query:
            self._list_files(self.app)
            return
        filtered = filter_by_query(self.files, query)
        sorted_filtered = sort_files(
            filtered, str(self.current_path), self.sort_var.get()
        )
        self._display_files(sorted_filtered)

    def _set_view_mode(self, mode: str) -> None:
        self.view_mode = mode
        if mode == "grid":
            self.grid_btn.configure(fg_color="blue")
            self.list_btn.configure(fg_color="gray30")
        else:
            self.grid_btn.configure(fg_color="gray30")
            self.list_btn.configure(fg_color="blue")
        self._list_files(self.app)

    def _on_sort_change(self, value) -> None:
        self._list_files(self.app)

    def _handle_click(self, event, r, master, boton, tool_tip=None) -> None:
        if not event.state & 0x0004:
            self._temp_items.clear()
            self.selected_objects.clear()

        if event.state & 0x0004:
            if self.method in (
                "askopenfilenames",
                "askopenfiles",
                "askdirectories",
                "askopenpathnames",
            ):
                if r not in self._temp_items:
                    self._temp_items.append(r)
                boton.configure(fg_color="blue")
                return
            if boton not in self._all_buttons:
                self._all_buttons.append(boton)
        else:
            self._temp_items.clear()
            if self.method in (
                "askopenfilenames",
                "askopenfiles",
                "askdirectories",
                "askopenpathnames",
            ):
                self._temp_items.append(r)
            for btn in self._all_buttons:
                if btn.winfo_exists():
                    btn.configure(
                        fg_color="transparent",
                        hover_color="#8da3ae",
                        text_color=self._text_color(),
                    )
            if os.path.isdir(r):
                self.navigate_to(path=r, master=master)
            else:
                self._temp_items.append(r)

    def _select_list_row(self, event, r, frame) -> None:
        if not event.state & 0x0004:
            self._temp_items.clear()
            self.selected_objects.clear()
            for row in self._selected_row_frames:
                if row.winfo_exists():
                    row.configure(
                        fg_color="#2f3136"
                        if self.current_theme.lower() == "dark"
                        else "#f7f7f7"
                    )
            self._selected_row_frames.clear()

        if self.method in (
            "askopenfilenames",
            "askopenfiles",
            "askdirectories",
            "askopenpathnames",
        ):
            if r not in self._temp_items:
                self._temp_items.append(r)
            if frame not in self._selected_row_frames:
                self._selected_row_frames.append(frame)
            frame.configure(fg_color="#2073d4")
            return


# Backward-compatible alias used by _functions / external code
_DrawApp = DrawApp
