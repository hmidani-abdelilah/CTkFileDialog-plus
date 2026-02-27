#!/usr/bin/env python
import os, re, cv2, time
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from pathlib import Path
from PIL import Image 
import tkinter as tk
from CTkToolTip import *
from typing import Any, Literal, Optional, TextIO, List
from _tkinter import TclError
from tkinter import ttk
import _tkinter 
from ._system import find_owner

class _CustomToolTip(CTkToolTip):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _show(self) -> None:
        if not self.widget.winfo_exists():
            self.hide()
            self.destroy()

        if self.status == "inside" and time.time() - self.last_moved >= self.delay:
            self.status = "visible"
            try: 
                self.deiconify()
            except _tkinter.TclError: 
                pass


class _System():
    
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetPath(path=None) -> str:
        if path is None:
            path = os.getcwd()
        return f"{path}" if path == os.getenv('HOME') else path
    
    @staticmethod
    def parse_path(path):
        
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

class _DrawApp():

    def __init__(self, 
                 method : str,
                 filetypes: Optional[List[str]] = None, 
                 bufering: int = 1,
                 encoding: str = 'utf-8',
                 current_path : str = '.',
                 hidden: bool = False, 
                 preview_img: bool = False,
                 autocomplete: bool = False,
                 video_preview: bool = False,
                 tool_tip: bool = False,
                 title: str = 'CTkFileDialog',
                 geometry: str = '1320x720') -> None:
        
        self.current_path = current_path

        if not self.current_path: 
            self.current_path = os.getcwd()
        else:
            self.current_path = _System.parse_path(path=self.current_path)
        self.autocomplete = autocomplete
        
        self.preview_img = preview_img
        self.bufering = bufering
        self.encoding = encoding
        self.hidden = hidden
        self.video_preview = video_preview
        self.suggest = []
        self.tool_tip = tool_tip
        self._all_buttons = []
        self.filetypes = filetypes
        self.tab_index = -1
        self._BASE_DIR = Path(__file__).parent
        self.method = method 
        self.current_theme = ctk.get_appearance_mode()
        self.view_mode = "grid"  # Default view mode
        self.display_files = []  # Files to display
        self.BATCH = 50  # Load files in batches of 50
        self.app = ctk.CTkToplevel()
        self.app.title(string=title)
        self.app.geometry(geometry)
        self.selected_file = '' 
        self.selected_objects : list = [] 
        self._load_icons()
        self._temp_item = None 
        self.app.protocol("WM_DELETE_WINDOW", self.protocol_windows)
        self._temp_items =  [] 
        self.TopSide(master=self.app)
        self.LeftSide(master=self.app)
        self.CenterSide(master=self.app)
        self.app.bind("<Alt-Left>", lambda _: self.btn_back(master=self.app))
        try: 
            self.app.grab_set()
        except _tkinter.TclError:
            pass

    def protocol_windows(self):

        try:
            self.app.destroy()

            self.app.unbind_all("<MouseWheel>")
        except  Exception:
            pass

    @staticmethod
    def _is_image(image : str) -> bool :
        try:

            with Image.open(image) as img:

                img.verify()

            return True
        except:
            return False
    def _load_icons(self):
        icon_path = self._BASE_DIR / "icons"  

        self.icons = {
            "folder": ctk.CTkImage(Image.open(icon_path / "folder.png"), size=(40, 40)),
            "bash": ctk.CTkImage(Image.open(icon_path / "bash.png"), size=(40, 40)),
            "image": ctk.CTkImage(Image.open(icon_path / "image.png"), size=(40, 40)),
            "python": ctk.CTkImage(Image.open(icon_path / "python.png"), size=(40, 40)),
            "text": ctk.CTkImage(Image.open(icon_path / "text.png"), size=(40, 40)),
            "markdown": ctk.CTkImage(Image.open(icon_path / "markdown.png"), size=(40, 40)),
            "javascript": ctk.CTkImage(Image.open(icon_path / "javascript.png"), size=(40, 40)),
            "php": ctk.CTkImage(Image.open(icon_path / "php.png"), size=(40, 40)),
            "html": ctk.CTkImage(Image.open(icon_path / "html.png"), size=(40, 40)),
            "css": ctk.CTkImage(Image.open(icon_path / "css.png"), size=(40, 40)),
            "ini": ctk.CTkImage(Image.open(icon_path / "ini.png"), size=(40, 40)),
            "conf": ctk.CTkImage(Image.open(icon_path / "conf.png"), size=(40, 40)),
            "exe": ctk.CTkImage(Image.open(icon_path / "exe.png"), size=(40, 40)),
            "odt": ctk.CTkImage(Image.open(icon_path / "odt.png"), size=(40, 40)),
            "pdf": ctk.CTkImage(Image.open(icon_path / "pdf.png"), size=(40, 40)),
            "json": ctk.CTkImage(Image.open(icon_path / "json.png"), size=(40, 40)),
            "gz": ctk.CTkImage(Image.open(icon_path / "gz.png"), size=(40, 40)),
            "video": ctk.CTkImage(Image.open(icon_path / "video.png"), size=(40, 40)),
            "awk": ctk.CTkImage(Image.open(icon_path / "bash.png"), size=(40, 40)),
            'webp': ctk.CTkImage(Image.open(icon_path / 'image.png'), size=(40, 40)),
            "default": ctk.CTkImage(Image.open(icon_path / "text.png"), size=(40, 40)),  # default icon
        }

        self.extension_icons = {
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
    
    def update_entry(self, path) -> None:
        self.PathEntry.configure(state='normal')
        self.PathEntry.delete(0, 'end')
        self.PathEntry.insert(0, path)

    def fix_name(self, name: str,
                 max_len : int = 18) -> str:

        if len(name) > max_len:

            return name[:max_len - 3]
        return name
    
    def btn_back(self, master: ctk.CTkToplevel):
        if self.current_path != os.path.dirname(self.current_path):
            self.current_path = os.path.dirname(self.current_path)
            self.update_entry(path=self.current_path)
            self._list_files(master)


    def navigate_to(self, path: str, master):
        try:
            path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
            
            # If it's a directory
            if os.path.isdir(path):
                if self.method == 'askdirectory':
                    self._temp_item = path
                self.current_path = Path(path)
                self.update_entry(path=self.current_path)
                self._list_files(master)
                return

            # If it's a file and we're in save-as mode
            if self.method in ['asksaveasfile', 'asksaveasfilename']:
                if os.path.isfile(path):
                    msg = CTkMessagebox(
                        message='This file exists. Do you want to overwrite it?',
                        icon='warning',
                        title='Warning',
                        option_1='Yes',
                        option_2='No'
                    )
                    if msg.get() == 'No':
                        return
                self._temp_item = path
                self.close_app()
                return

            if self.method == 'askopenfile':
                if not os.path.isfile(path):
                    
                    CTkMessagebox(message='File not found!', title='Error', icon='cancel')
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

            self.PathEntry.delete(0, 'end')
            self.PathEntry.insert(0, str(self.current_path))
            self.PathEntry.configure(state='normal')
            
            CTkMessagebox(message='No such file or directory!', title='Error', icon='cancel')
            return

        except PermissionError:
            
            CTkMessagebox(message='Permission denied!', title='Error', icon='cancel')
        except FileNotFoundError: 
            
            CTkMessagebox(message='File Not Found!', title='Error', icon='cancel')

    def close_app(self):
        if self.method == 'asksaveasfilename':
            if not os.path.isdir(self.PathEntry.get()): self.selected_file = self.PathEntry.get()

        if self._temp_item:
            self.protocol_windows() 
            self.app.destroy()
            if self.method == 'asksaveasfile':
                self.selected_file = self._temp_item
                return 
            elif self.method == 'askopenfile':
                self.selected_file = self._temp_item
            else:
                self.selected_file = self._temp_item
                return

        if len(self._temp_items) >= 1:
            self.protocol_windows()
            self.app.destroy()
            if self.method == "askopenfilenames" or self.method ==  "askopenfiles":
                seen = set()
                self.selected_objects = [
                    f for f in self._temp_items
                    if not os.path.isdir(f) and f not in seen and not seen.add(f)
                ]
                
                return
            
    
    @staticmethod
    def _is_video(video: str):

        try:

            cap = cv2.VideoCapture(video)
            valid = cap.isOpened()
            cap.release()
            return valid 
        except:

            return False
                

    def _autocomplete(self, event):        

        if not hasattr(self, "entire_paths"):
            return "break"

        if not self.entire_paths:

            return "break"

        if not self.files:
            return "break"


        max_index = len(self.files)

        if event.keysym == 'Up':
            self.tab_index = (self.tab_index - 1) % max_index
        else:
            self.tab_index = (self.tab_index + 1) % max_index

        path = self.entire_paths[self.tab_index]
        self.PathEntry.delete(0, ctk.END)
        self.PathEntry.insert(0, path)
        
        self._temp_item = path 

        return "break"

    def TopSide(self, master: ctk.CTkToplevel) -> None:
        TopBar = ctk.CTkFrame(master=master, height=40, fg_color="transparent")
        TopBar.pack(side='top', fill='x')
        
        def btn_exit():
            msg = CTkMessagebox(message='Do you want to exit?', title='Exit', option_1='Yes', option_2='No', icon='warning')
            if msg.get() == 'Yes':
                self.protocol_windows()

                self.selected_file = None 
                self.selected_objects = []
                self._temp_item = None 
                self._temp_items = []
                master.destroy()
                return 

        # Exit button
        ButtonExit = ctk.CTkButton(master=TopBar, text='Exit', font=('Hack Nerd Font', 15), width=70, command=btn_exit, hover_color='red')
        ButtonExit.pack(side='left', fill='x')

         # Path field
        self.PathEntry = ctk.CTkEntry(master=TopBar, width=1070, corner_radius=0, insertwidth=0)
        self.PathEntry.insert(index=0, string=_System.GetPath(str(self.current_path)))
        self.PathEntry.pack(side='right', fill='y', padx=10, pady=10)
        self.PathEntry.bind('<Return>', command = lambda _: self.navigate_to(path=self.PathEntry.get(), master=master))
      
        # Back button
        ButtonBack = ctk.CTkButton(master=TopBar, text='', font=('Hack Nerd Font', 15), width=70, command = lambda path=self.PathEntry.get(): self.btn_back(master=master))
        ButtonBack.pack(side='left', fill='x', padx=10, pady=10)

        # Ok button
        ButtonOk = ctk.CTkButton(master=TopBar, text='Ok', font=('Hack Nerd Font', 15), width=70, command = lambda: self.close_app())
        ButtonOk.pack(side='left', fill='x', padx=10, pady=10)

        if self.autocomplete:
            
            self.PathEntry.bind('<Down>', lambda event: self._autocomplete(event))
            self.PathEntry.bind('<Up>', lambda event: self._autocomplete(event))
            self.PathEntry.bind('<Tab>', lambda event: self._autocomplete(event))
        
        # Search bar
        self.SearchFrame = ctk.CTkFrame(master=master, fg_color="transparent", height=40)
        self.SearchFrame.pack(side='top', fill='x', padx=10, pady=(5, 10))
        
        search_label = ctk.CTkLabel(self.SearchFrame, text="Search:", font=("Arial", 12))
        search_label.pack(side="left", padx=(0, 10))
        
        self.SearchEntry = ctk.CTkEntry(self.SearchFrame, placeholder_text="Type to search files...")
        self.SearchEntry.pack(expand=True, fill="x", side="left", padx=(0, 20))
        self.SearchEntry.bind('<KeyRelease>', lambda _: self._search_files_default())
        
        # View mode toggle (Grid/List)
        self.view_mode = "grid"
        view_label = ctk.CTkLabel(self.SearchFrame, text="View:", font=("Arial", 12))
        view_label.pack(side="left", padx=(0, 10))
        
        self.grid_btn = ctk.CTkButton(self.SearchFrame, text="📊 Grid", width=60, 
                                       command=lambda: self._set_view_mode("grid"))
        self.grid_btn.pack(side="left", padx=5)
        
        self.list_btn = ctk.CTkButton(self.SearchFrame, text="📋 List", width=60,
                                       command=lambda: self._set_view_mode("list"))
        self.list_btn.pack(side="left", padx=5)
        
        # Sort dropdown
        sort_label = ctk.CTkLabel(self.SearchFrame, text="Sort:", font=("Arial", 12))
        sort_label.pack(side="left", padx=(20, 10))
        
        self.sort_var = ctk.StringVar(value="name")
        self.sort_menu = ctk.CTkOptionMenu(
            self.SearchFrame,
            values=["name", "date", "type", "size", "modified"],
            command=self._on_sort_change,
            variable=self.sort_var
        )
        self.sort_menu.pack(side="left", padx=5)
    
    def _get_video_frame(self, path: str, frame_number: int = 1) -> Image.Image | None:
        if not self._is_video(path):
            return None

        try:
            cap = cv2.VideoCapture(path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame)
        except:
            return None
    
         
    def LeftSide(self, master) -> None:

        # Main frame
        LeftSideFrame = ctk.CTkFrame(master=master, width=200)
        LeftSideFrame.pack(side='left', fill='y', padx=10, pady=10)
        LeftSideFrame.pack_propagate(False)

        # Start with the user's HOME directory
        home = os.path.expanduser("~")
        folders = {f"{str(os.getenv('HOME')).replace('/home/', '')}": home}

        # Load the user-dirs.dirs file
        dir_file = os.path.join(home, ".config/user-dirs.dirs")
        pattern = re.compile(r'XDG_\w+_DIR="(.+?)"')
        
        import platform
        if platform.system() == 'Linux':
            if not os.path.exists(path=dir_file):
                raise FileNotFoundError(f"The file {dir_file} is required for the program to run!")
            with open(dir_file, 'r') as f:
                for line in f:
                    if not line.startswith('#') and line.strip():
                        match = pattern.search(line)
                        if match:
                            path = os.path.expandvars(match.group(1))
                            name = os.path.basename(os.path.normpath(path))
                            if name != f"{os.getenv('USER')}":  # Avoid duplicate
                                folders[name] = path

        elif platform.system() == 'Windows':
            home = Path.home()
            win_folders = {
                home.name: str(home),  
                "Desktop": home / "Desktop",
                "Documents": home / "Documents",
                "Downloads": home / "Downloads",
                "Pictures": home / "Pictures",
                "Music": home / "Music",
                "Videos": home / "Videos",
            }

            folders = {}
            folders = {k: v  for k, v in win_folders.items()}

        # Title
        LabelSide = ctk.CTkLabel(master=LeftSideFrame, text='Places', font=('Hack Nerd Font', 15))
        LabelSide.pack(side=ctk.TOP, padx=5, pady=5)

        icons = {
            os.getenv("USER"): "",  # user's HOME
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
            icon = icons.get(name, "")  
            button_text = f"    {icon}  {name}"  
            DirectorySide = ctk.CTkButton(
                master=LeftSideFrame,
                text=button_text,
                font=("Hack Nerd Font", 14),
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                corner_radius=2,
                border_width=0,
                command=lambda r=path, n=name: self.navigate_to(path=r, master=master)
            )
            DirectorySide.pack(fill="x", pady=4)


    def event_scroll(self):
        
        canvas = self.CenterSideFrame._parent_canvas

        def _on_mousewheel(event):
            try:
                x_root, y_root = event.x_root, event.y_root

                # Coordinates and size of the scrollable frame
                x1 = self.CenterSideFrame.winfo_rootx()
                y1 = self.CenterSideFrame.winfo_rooty()
                x2 = x1 + self.CenterSideFrame.winfo_width()
                y2 = y1 + self.CenterSideFrame.winfo_height()
                if x1 <= x_root <= x2 and y1 <= y_root <= y2:

                    if event.num == 4: 
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:  
                        canvas.yview_scroll(1, "units")
                    else:  
                        canvas.yview_scroll(-int(event.delta / 120), "units")
                    
                    # Trigger lazy loading check
                    self._check_scroll(self.app)
                    return "break"
            except Exception as e:
                pass

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Bind to all child widgets
        for widget in canvas.winfo_children():
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)


    def CenterSide(self, master: ctk.CTkToplevel) -> None:
        self.CenterSideFrame = ctk.CTkScrollableFrame(master=master)
        self.CenterSideFrame.pack(expand=True, side='top', fill='both', padx=10, pady=10)
        
        
        self.event_scroll()

        self.content_frame = ctk.CTkFrame(master=self.CenterSideFrame)
        self.content_frame.pack(side='top', fill='both', expand=True, padx=20, pady=10)

        self._list_files(master=master)

    def __clear__(self):

        for widget in self.content_frame.winfo_children():
            try: 
                widget.destroy()
            except (_tkinter.TclError, Exception):
                pass

    def _handle_click(self, event, r, master, boton, tool_tip=None):
        if not event.state & 0x0004: 
            self._temp_items.clear()
            self.selected_objects.clear()

        if event.state & 0x0004:

            if self.method in  ['askopenfilenames', 'askopenfiles']:
                if r not in self._temp_items: 
                    self._temp_items.append(r)
                boton.configure(fg_color="blue")
                return 

            if boton not in self._all_buttons: 
                self._all_buttons.append(boton)


        else:
            self._temp_items.clear()
            if self.method in ['askopenfilenames', 'askopenfiles']:
                self._temp_items.append(r)

            for btn in self._all_buttons:
                if btn.winfo_exists():
                    btn.configure(fg_color="transparent",
                    hover_color="#8da3ae",
                    text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
        )
            if os.path.isdir(r): 
                self.navigate_to(path=r, master=master)
            else:
                self._temp_items.append(r)

    @staticmethod
    def _get_info(path: str) -> str:
        try:
            st = os.stat(path)

            # owner user
            owner = find_owner(path)

            # Permissions (e.g., -rw-r--r--)
            #permissions = get_permissions(path)
    
            # readable date
            fecha = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))
    
            return f"""File: {os.path.basename(path)}
    creation: {fecha}
    owner: {owner}
    path: {path}
                    """
        except Exception as e:
            return f"Error getting info: {e}"

    
    def _load_files(self, master: Any, cantidad: int): 
        columnas = 5
        row = self.LOADED // columnas
        col = self.LOADED % columnas
        path = self.current_path

        while self.LOADED < len(self.files) and cantidad > 0:
            
            file = self.files[self.LOADED]
            full_path = os.path.join(path, file)

            if self.method == 'askdirectory' and os.path.isfile(full_path):
                self.LOADED += 1
                continue

            # Get icon based on file type
            if os.path.isdir(full_path):
                icon = self.icons["folder"]
            else:
                if self.preview_img and self._is_image(full_path):
                    try:
                        img = Image.open(full_path)
                        img.thumbnail((32, 32))
                        icon = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                    except:
                        icon = self.icons.get("image", self.icons["default"])
                elif self.video_preview and self._is_video(full_path):
                    frame = self._get_video_frame(full_path, frame_number=10)
                    if frame:
                        frame.thumbnail((32, 32))
                        icon = ctk.CTkImage(light_image=frame, dark_image=frame, size=(32, 32))
                    else:
                        icon = self.icons.get("video", self.icons["default"])
                else:
                    ext = os.path.splitext(file)[1].lower()
                    icon_key = self.extension_icons.get(ext, "default")
                    icon = self.icons.get(icon_key, self.icons["default"])

            fixed_name = self.fix_name(name=file)

            command = None
            if self.method not in ['askopenfilenames']:
                command = lambda r=full_path: self.navigate_to(path=r, master=master)
        
            boton = ctk.CTkButton(
                master=self.content_frame,
                text=fixed_name,
                image=icon,
                compound="left",
                width=180,
                height=60,
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                command=command
            )

            if self.tool_tip:
                _CustomToolTip(widget=boton, message=self._get_info(full_path))
            if self.method in ['askopenfilenames', 'askopenfiles']:
                boton.bind('<Button-1>', lambda event, r=full_path, b=boton: self._handle_click(event, r, master, b))
            boton.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= columnas:
                col = 0
                row += 1

            self.LOADED += 1
            cantidad -= 1

    def _check_scroll(self, master):
        try: 
            canvas = self.CenterSideFrame._parent_canvas
            yview = canvas.yview()
            
            # Ensure display_files exists
            if not hasattr(self, 'display_files') or not self.display_files:
                return
            
            # When user scrolls near the bottom, load more files
            if yview[1] > 0.80 and self.LOADED < len(self.display_files):
                if self.view_mode == "grid":
                    self._load_grid_files(self.BATCH)
                else:
                    self._load_list_files(self.BATCH)
        except _tkinter.TclError:
             pass
    
    def _search_files_default(self):
        # Only search if files have been loaded
        if not hasattr(self, 'files') or not self.files:
            return
        
        search_query = self.SearchEntry.get().lower()
        
        # Clear current display
        self.__clear__()
        
        if not search_query:
            # If search is empty, reload all files
            self._list_files(self.app)
            return
        
        # Filter files based on search query
        filtered_files = [f for f in self.files if search_query in f.lower()]
        
        # Display sorted results with lazy loading
        sorted_filtered = self._sort_files(filtered_files)
        self._display_files(sorted_filtered)
    
    def _set_view_mode(self, mode: str):
        """Toggle between grid and list view"""
        self.view_mode = mode
        
        # Update button styles
        if mode == "grid":
            self.grid_btn.configure(fg_color="blue")
            self.list_btn.configure(fg_color="gray30")
        else:
            self.grid_btn.configure(fg_color="gray30")
            self.list_btn.configure(fg_color="blue")
        
        # Refresh display
        self._list_files(self.app)
    
    def _on_sort_change(self, value):
        """Handle sort option change"""
        self._list_files(self.app)
    
    def _sort_files(self, files: list) -> list:
        """Sort files based on selected criteria"""
        sort_by = self.sort_var.get()
        current_path = self.current_path
        
        def get_file_info(filename):
            full_path = os.path.join(current_path, filename)
            try:
                stat_info = os.stat(full_path)
                return {
                    'name': filename.lower(),
                    'date': stat_info.st_mtime,
                    'modified': stat_info.st_mtime,
                    'type': os.path.splitext(filename)[1].lower(),
                    'size': stat_info.st_size,
                    'is_dir': os.path.isdir(full_path)
                }
            except:
                return {
                    'name': filename.lower(),
                    'date': 0,
                    'modified': 0,
                    'type': '',
                    'size': 0,
                    'is_dir': os.path.isdir(full_path)
                }
        
        # Sort: directories first, then by selected criteria
        sorted_files = sorted(
            files,
            key=lambda f: (not get_file_info(f)['is_dir'], get_file_info(f).get(sort_by, 0))
        )
        
        return sorted_files
    
    def _display_files(self, files: list):
        """Display files in current view mode (rollback: load all at once)."""
        # Store files and load all at once to restore previous behavior
        self.display_files = files
        self.LOADED = 0

        total = len(files)
        if total <= 0:
            return

        # Load all items immediately
        if self.view_mode == "grid":
            self._load_grid_files(total)
        else:
            self._load_list_files(total)
    
    def _load_grid_files(self, cantidad: int):
        """Incrementally load grid view files"""
        columnas = 5
        
        while self.LOADED < len(self.display_files) and cantidad > 0:
            file = self.display_files[self.LOADED]
            
            if self.method == 'askdirectory' and os.path.isfile(os.path.join(self.current_path, file)):
                self.LOADED += 1
                continue
            
            full_path = os.path.join(self.current_path, file)
            
            # Get icon
            if os.path.isdir(full_path):
                icon = self.icons["folder"]
            else:
                if self.preview_img and self._is_image(full_path):
                    try:
                        img = Image.open(full_path)
                        img.thumbnail((32, 32))
                        icon = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                    except:
                        icon = self.icons.get("image", self.icons["default"])
                elif self.video_preview and self._is_video(full_path):
                    frame = self._get_video_frame(full_path, frame_number=10)
                    if frame:
                        frame.thumbnail((32, 32))
                        icon = ctk.CTkImage(light_image=frame, dark_image=frame, size=(32, 32))
                    else:
                        icon = self.icons.get("video", self.icons["default"])
                else:
                    ext = os.path.splitext(file)[1].lower()
                    icon_key = self.extension_icons.get(ext, "default")
                    icon = self.icons.get(icon_key, self.icons["default"])
            
            fixed_name = self.fix_name(name=file)
            
            command = None
            if self.method not in ['askopenfilenames']:
                command = lambda r=full_path: self.navigate_to(path=r, master=self.app)
            
            row = self.LOADED // columnas
            col = self.LOADED % columnas
            
            boton = ctk.CTkButton(
                master=self.content_frame,
                text=fixed_name,
                image=icon,
                compound="left",
                width=180,
                height=60,
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                command=command
            )
            
            if self.tool_tip:
                _CustomToolTip(widget=boton, message=self._get_info(full_path))
            if self.method in ['askopenfilenames', 'askopenfiles']:
                boton.bind('<Button-1>', lambda event, r=full_path, b=boton: self._handle_click(event, r, self.app, b))
            boton.grid(row=row, column=col, padx=10, pady=10)
            
            self.LOADED += 1
            cantidad -= 1
        
        # Force update scroll region
        try:
            self.content_frame.update_idletasks()
            self.CenterSideFrame._parent_canvas.configure(scrollregion=self.CenterSideFrame._parent_canvas.bbox("all"))
        except:
            pass

    def _show_load_more_button(self):
        """Show a manual 'Load more' button at the end of the content frame."""
        try:
            if hasattr(self, '_load_more_btn') and getattr(self, '_load_more_btn') and self._load_more_btn.winfo_exists():
                return

            self._load_more_btn = ctk.CTkButton(master=self.content_frame, text="Load more",
                                                command=self._on_load_more)
            # place it at the bottom of the content frame
            self._load_more_btn.pack(side='top', pady=10)
        except Exception:
            pass

    def _remove_load_more_button(self):
        """Remove the manual 'Load more' button if present."""
        try:
            if hasattr(self, '_load_more_btn') and getattr(self, '_load_more_btn') and self._load_more_btn.winfo_exists():
                try:
                    self._load_more_btn.destroy()
                except Exception:
                    pass
            if hasattr(self, '_load_more_btn'):
                try:
                    del self._load_more_btn
                except Exception:
                    pass
        except Exception:
            pass

    def _on_load_more(self):
        """Handler for the manual load-more button."""
        try:
            remaining = len(self.display_files) - self.LOADED
            if remaining <= 0:
                self._remove_load_more_button()
                return

            cantidad = self.BATCH if remaining >= self.BATCH else remaining
            if self.view_mode == 'grid':
                self._load_grid_files(cantidad)
            else:
                self._load_list_files(cantidad)

            # If we've finished loading, remove the button
            if self.LOADED >= len(self.display_files):
                self._remove_load_more_button()
        except Exception:
            pass
    
    def _load_list_files(self, cantidad: int):
        """Incrementally load list view files"""
        while self.LOADED < len(self.display_files) and cantidad > 0:
            file = self.display_files[self.LOADED]
            
            if self.method == 'askdirectory' and os.path.isfile(os.path.join(self.current_path, file)):
                self.LOADED += 1
                continue
            
            full_path = os.path.join(self.current_path, file)
            
            # Get file info
            try:
                stat_info = os.stat(full_path)
                file_size = stat_info.st_size
                mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat_info.st_mtime))
            except:
                file_size = 0
                mod_time = "N/A"
            
            is_dir = os.path.isdir(full_path)
            file_type = "Directory" if is_dir else os.path.splitext(file)[1][1:].upper() or "File"
            
            # Get icon
            if is_dir:
                icon = self.icons["folder"]
            else:
                ext = os.path.splitext(file)[1].lower()
                icon_key = self.extension_icons.get(ext, "default")
                icon = self.icons.get(icon_key, self.icons["default"])
            
            # Size formatting
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Create list item frame
            item_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=40)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            # Icon
            icon_label = ctk.CTkLabel(item_frame, image=icon, text="")
            icon_label.pack(side="left", padx=10)
            
            # File name and details
            info_text = f"{file}\n{file_type} • {size_str} • {mod_time}"
            
            command = None
            if self.method not in ['askopenfilenames']:
                command = lambda r=full_path: self.navigate_to(path=r, master=self.app)
            
            boton = ctk.CTkButton(
                master=item_frame,
                text=info_text,
                compound="left",
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color="#000000" if self.current_theme.lower() == 'light' else '#cccccc',
                command=command,
                font=("Arial", 11)
            )
            boton.pack(expand=True, fill="both", side="left")
            
            if self.method in ['askopenfilenames', 'askopenfiles']:
                boton.bind('<Button-1>', lambda event, r=full_path, b=boton: self._handle_click(event, r, self.app, b))
            
            self.LOADED += 1
            cantidad -= 1
        
        # Force update scroll region
        try:
            self.content_frame.update_idletasks()
            self.CenterSideFrame._parent_canvas.configure(scrollregion=self.CenterSideFrame._parent_canvas.bbox("all"))
        except:
            pass


    def _list_files(self, master: ctk.CTkToplevel) -> None:
        self.LOADED = 0
        self.BATCH = 50
        self.selected_objects.clear()
        self._all_buttons.clear()

        self.CenterSideFrame._parent_canvas.yview_moveto(0)
        self.__clear__()

        path = self.current_path

        self.files = [
            f.name for f in os.scandir(path)
            if (
                (f.is_dir() or (self.method != 'askdirectory' and f.is_file())) and
                (self.hidden or not f.name.startswith('.')) and
                (f.is_dir() or not self.filetypes or
                 any(f.name.endswith(ext) for ext in self.filetypes))
            )
        ]

        if not self.files:
            self.display_files = []
            return

        if self.autocomplete:
            self.entire_paths = [os.path.join(self.current_path, f) for f in self.files]

            if not self.entire_paths:
                self.entire_paths = None
        
        # Sort files before displaying
        sorted_files = self._sort_files(self.files)
        self._display_files(sorted_files)


class _MiniDialog():

    def __init__(self, 
                 method: str,
                 hidden: bool = False,
                 filetypes: Optional[List[str]] = None,
                 autocomplete: bool = False,
                 initial_dir: str = '.',
                 _extra_method: str = '',
                 geometry: str = '500x400',
                 title: str = 'CTkFileDialog'):
        
        self.master = ctk.CTkToplevel()
        self.master.geometry(geometry_string=geometry)
        self.master.title(title)
        self._extra_method = _extra_method
        self.tab_index = -1 
        self.method = method 
        self.hidden = hidden 
        self.filetypes = filetypes
        self.autocomplete = autocomplete
        self.initial_dir = initial_dir

        if not self.initial_dir: 
            self.initial_dir = os.getcwd()
        else: 
            self.initial_dir = _System().GetPath(path=self.initial_dir)

        self.selected_path = ''
        self.selected_paths = []
        self.selected_items = []
        self.selected_item = ''
        
        # Load images 
        self._PATH = os.path.dirname(os.path.realpath(__file__))

        self.folder_image = self._load_image(image=os.path.join(self._PATH, 'icons/_IconsMini/folder.png'))
    
        self.file_image = self._load_image(image=os.path.join(self._PATH, "icons/_IconsMini/file.png"))
        
        self._TopSide()

        self._CenterSide()
        
        self.list_files()
        self.master.bind("<Alt-Left>", lambda _: self._up() )

        self.master.wait_visibility()
        self.master.grab_set()
        self.master.wait_window()

    
    def _get_path(self):

        return os.path.abspath(os.path.expandvars(os.path.expanduser(self.initial_dir)))

    def _TopSide(self):

        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        self.path_frame = ctk.CTkFrame(self.frame)
        self.path_frame.pack(fill=ctk.X, padx=10, pady=10)

        self.path_entry = ctk.CTkEntry(self.path_frame, )
        self.path_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT, padx=10, pady=10)
        self.path_entry.bind('<Return>', lambda _: self._on_enter_path())
        self.path_entry.insert(0, self._get_path())

        if self.autocomplete: 
            for bind in ['<Tab>', '<Down>', '<Up>']:
                self.path_entry.bind(bind, self._autocomplete)

        self.up_btn = ctk.CTkButton(
            self.path_frame, text="↑", width=30, command=self._up
        )

        self.up_btn.pack(side=ctk.RIGHT, padx=10, pady=10)
        
        # Search bar
        self.search_frame = ctk.CTkFrame(self.frame)
        self.search_frame.pack(fill=ctk.X, padx=10, pady=(0, 10))
        
        search_label = ctk.CTkLabel(self.search_frame, text="Search:", font=("Arial", 12))
        search_label.pack(side=ctk.LEFT, padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Type to search files...")
        self.search_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT)
        self.search_entry.bind('<KeyRelease>', lambda _: self._search_files())
        btn_frame = ctk.CTkFrame(self.frame, fg_color='transparent')
        btn_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)

        ok_btn = ctk.CTkButton(btn_frame, text="OK", command=self._on_select)
        ok_btn.pack(side=ctk.RIGHT)

        ctk.CTkButton(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side=ctk.RIGHT, padx=10
        )

    def list_files(self):
        path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path_entry.get())))
        if os.path.isfile(path):
            return
        try:
            try:
                for item in self.tree.get_children():
                    self.tree.delete(item)
            except TclError:
                return

            self.files = {'name': [], 'path': []}
            filtered = []

            for f in os.scandir(path):
                if (
                    (f.is_dir() or (self.method != 'askdirectory' and f.is_file())) and
                    (self.hidden or not f.name.startswith('.')) and
                    (f.is_dir() or not self.filetypes or
                     any(f.name.endswith(ext) for ext in self.filetypes))
                ):
                    filtered.append(f)
                    self.files['name'].append(f.name)
                    self.files['path'].append(f.path)

            sorted_files = sorted(
                filtered,
                key=lambda f: (not f.is_dir(), f.name.lower())
            )

            self.update_entry(path=path)

            for f in sorted_files:
                icon = self.folder_image if f.is_dir() else self.file_image
                self.tree.insert("", tk.END, text=f.name, image=icon)

            if self.autocomplete:
                self.absolute_paths = [f.path for f in sorted_files]

        except PermissionError:
            CTkMessagebox(message='Permission Denied!', title='Error', icon='cancel')
            self._on_cancel(destroy=False)
        else:
            if self.autocomplete:
                self.max_index = len(self.files['name'])


    def update_entry(self, path):
            self.path_entry.configure(state='normal')
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, path)
    
    def _autocomplete(self, event: tk.Event):

        if not self.files['name'] or not hasattr(self, "max_index"):
            return "break"

        if event.keysym == 'Up':
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

    def _on_enter_path(self):
        path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path_entry.get())))

        if os.path.isdir(path):
            self.initial_dir = path
            self.list_files()
        else: 
            if os.path.isfile(path):
                return 

            self.path_entry.configure(state='normal')

            if not os.path.exists(path=path):

                self._on_cancel(destroy=False)
                self.update_entry(path=self.initial_dir)
                CTkMessagebox(title="Error", icon='cancel', message='No such file or directory!')

            return ""


    def _on_cancel(self, destroy: bool = True):
        self.selected_path = None 
        self.selected_item = None 

        self.selected_paths = None 
        self.selected_items = None
        if destroy:
            self.master.destroy()
        return 

    def _CenterSide(self):
        self.tree_frame = ctk.CTkFrame(self.frame)
        self.tree_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use('clam')
        mode = ctk.get_appearance_mode()

        if mode == 'Dark':
            style.configure("Treeview",
                            background="#242424",
                            foreground="#FFFFFF",
                            fieldbackground="#242424",
                            bordercolor="#242424",
                            rowheight=30)
            style.map("Treeview",
                background=[('selected', '#444444')],
                foreground=[('selected', '#FFFFFF')])
        else:  # Light mode
            style.configure("Treeview",
                            background="#FFFFFF",
                            foreground="#000000",
                            fieldbackground="#FFFFFF",
                            bordercolor="#DDDDDD",
                            rowheight=30)
            style.map("Treeview",
                background=[('selected', '#E0E0E0')],
                foreground=[('selected', '#000000')])
        self.tree = ttk.Treeview(self.tree_frame, show="tree", selectmode='extended' if self.method in ['askopenfilenames', 'askopenfiles'] else 'browse')
        self.tree.bind("<Double-1>", self._on_click)
        self.tree.bind("<Button-1>", self._on_select_item)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _load_image(self, image: str) -> tk.PhotoImage:
        
        return tk.PhotoImage(file=image)
    
    def _search_files(self):
        # Only search if files have been loaded
        if not hasattr(self, 'files') or not self.files['name']:
            return
        
        search_query = self.search_entry.get().lower()
        
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_query:
            # If search is empty, reload all files
            self.list_files()
            return
        
        # Filter files based on search query
        self.filtered_paths = []
        for name, path in zip(self.files['name'], self.files['path']):
            if search_query in name.lower():
                is_dir = os.path.isdir(path)
                icon = self.folder_image if is_dir else self.file_image
                self.tree.insert("", tk.END, text=name, image=icon)
                self.filtered_paths.append(path)
        
        # Store the filtered paths so _on_select_item and _on_click can use them
        self.absolute_paths = self.filtered_paths
    
    def _on_select(self):

        path = self.path_entry.get().strip() if hasattr(self, "path_entry") else ""

        if path:
            path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
            if not os.path.dirname(path):
                path = os.path.join(self.initial_dir, path)

        if self.method in ['asksaveasfile', 'asksaveasfilename']:
            if not path or os.path.isdir(path):
                return

            if os.path.exists(path) and self._extra_method != 'askopenfile':
                opts = CTkMessagebox(
                    message='This file already exists! Do you want to overwrite it?',
                    title='Error',
                    icon='warning',
                    option_1='Yes',
                    option_2='No'
                )
                if opts.get() == 'No':
                    return

            self.selected_path = path
            self.master.destroy()
            return

        elif self.method in ['askopenfiles', 'askopenfilenames']:
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

        elif self.method in ['askopenfilename', 'askopenfile', 'askdirectory']:
            if not self.selected_item:
                return

            if self.method == 'askdirectory' and os.path.isdir(self.selected_item):
                self.selected_path = self.selected_item
                self.master.destroy()
                return

            elif self.method in ['askopenfilename', 'askopenfile'] and os.path.isfile(self.selected_item):
                self.selected_path = self.selected_item
                self.master.destroy()
                return

    def _on_select_item(self, event=None):
        selected_item = self.tree.focus()
        items = self.tree.get_children()

        if not selected_item or not items:
            return

        try:
            idx = items.index(selected_item)
            if hasattr(self, 'absolute_paths') and idx < len(self.absolute_paths):
                self.selected_item = self.absolute_paths[idx]
        except (ValueError, IndexError):
            pass

    def _on_click(self, event=None):
        selected_item = self.tree.focus()
        items = self.tree.get_children()

        if not selected_item:
            return 

        idx = items.index(selected_item)
        self.selected_item = self.absolute_paths[idx]

        if os.path.isdir(self.selected_item):
            self.initial_dir = self.selected_item 
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, self.selected_item)
            self.list_files()
            return  

        # If it's a file:
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.selected_item)


    def _up(self):
        current_path = os.path.abspath(os.path.expandvars(os.path.expanduser(self.initial_dir)))

        self.initial_dir = os.path.dirname(current_path)

        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, self.initial_dir)

        self.list_files()
