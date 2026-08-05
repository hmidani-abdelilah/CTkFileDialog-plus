#!/usr/bin/env python
import os
from pathlib import Path
import customtkinter as ctk
from CTkFileDialog import (
    askopenfilename,
    askopenfile,
    askopenfiles,
    askopenfilenames,
    askdirectory,
    askopendirname,
    askopendirnames,
    askopenpathname,
    askopenpathnames,
    asksaveasfilename,
    asksaveasfile,
)

HOME = os.path.expanduser("~")
FILETYPES = [("Text files", "*.txt"), ("Python files", "*.py *.pyw"), ("All files", "*.*")]


def format_result(value):
    if value is None:
        return "No selection"
    if isinstance(value, (tuple, list)):
        if not value:
            return "No selection"
        items = []
        for item in value:
            if hasattr(item, "name"):
                items.append(item.name)
            else:
                items.append(str(item))
        return "\n".join(items)
    if hasattr(value, "name"):
        return value.name
    return str(value)


def show_result(title, value):
    display_text = f"{title}\n\n{format_result(value)}"
    result_label.configure(text=display_text)


def open_single_file(style: str):
    result = askopenfilename(
        style=style,
        filetypes=FILETYPES,
        autocomplete=True,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenfilename ({style})",
    )
    show_result("askopenfilename", result)


def open_multiple_files(style: str):
    result = askopenfilenames(
        style=style,
        filetypes=FILETYPES,
        autocomplete=True,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenfilenames ({style})",
    )
    show_result("askopenfilenames", result)


def open_file_object(style: str):
    file_obj = askopenfile(
        style=style,
        filetypes=FILETYPES,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenfile ({style})",
    )
    try:
        show_result("askopenfile", file_obj)
    finally:
        if file_obj is not None:
            file_obj.close()


def open_file_objects(style: str):
    file_objs = askopenfiles(
        style=style,
        filetypes=FILETYPES,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenfiles ({style})",
    )
    try:
        show_result("askopenfiles", file_objs)
    finally:
        if file_objs:
            for f in file_objs:
                try:
                    f.close()
                except Exception:
                    pass


def save_filename(style: str):
    result = asksaveasfilename(
        style=style,
        filetypes=FILETYPES,
        defaultext=".txt",
        initial_dir=HOME,
        title=f"asksaveasfilename ({style})",
    )
    show_result("asksaveasfilename", result)


def save_file_object(style: str):
    file_obj = asksaveasfile(
        style=style,
        mode="w",
        filetypes=FILETYPES,
        defaultext=".txt",
        initial_dir=HOME,
        title=f"asksaveasfile ({style})",
    )
    try:
        show_result("asksaveasfile", file_obj)
        if file_obj is not None:
            file_obj.write("CTkFileDialog write test\n")
    finally:
        if file_obj is not None:
            file_obj.close()


def select_directory(style: str):
    result = askdirectory(
        style=style,
        autocomplete=True,
        initial_dir=HOME,
        title=f"askdirectory ({style})",
    )
    show_result("askdirectory", result)


def select_directory_name(style: str):
    result = askopendirname(
        style=style,
        autocomplete=True,
        initial_dir=HOME,
        title=f"askopendirname ({style})",
    )
    show_result("askopendirname", result)


def select_directory_names(style: str):
    result = askopendirnames(
        style=style,
        autocomplete=True,
        initial_dir=HOME,
        title=f"askopendirnames ({style})",
    )
    show_result("askopendirnames", result)


def open_path_name(style: str):
    result = askopenpathname(
        style=style,
        filetypes=FILETYPES,
        autocomplete=True,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenpathname ({style})",
    )
    show_result("askopenpathname", result)


def open_path_names(style: str):
    result = askopenpathnames(
        style=style,
        filetypes=FILETYPES,
        autocomplete=True,
        preview_img=True,
        initial_dir=HOME,
        title=f"askopenpathnames ({style})",
    )
    show_result("askopenpathnames", result)


def toggle_theme():
    if theme_switch.get() == 1:
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")


def build_button(frame, text, command):
    return ctk.CTkButton(master=frame, text=text, command=command, width=260)


def main() -> None:
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.title("CTkFileDialog Full Function Test")
    app.geometry("820x780")

    container = ctk.CTkFrame(master=app, corner_radius=15)
    container.pack(padx=20, pady=20, fill="both", expand=True)

    header = ctk.CTkLabel(
        master=container,
        text="CTkFileDialog All-Function Example",
        font=("Arial", 20, "bold")
    )
    header.pack(pady=(10, 18))

    button_frame = ctk.CTkFrame(master=container)
    button_frame.pack(padx=10, pady=10, fill="x")

    build_button(button_frame, "askopenfilename (Default)", lambda: open_single_file("Default")).grid(row=0, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenfilename (Mini)", lambda: open_single_file("Mini")).grid(row=0, column=1, padx=10, pady=8)
    build_button(button_frame, "askopenfilenames (Default)", lambda: open_multiple_files("Default")).grid(row=1, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenfilenames (Mini)", lambda: open_multiple_files("Mini")).grid(row=1, column=1, padx=10, pady=8)
    build_button(button_frame, "askopenfile (Default)", lambda: open_file_object("Default")).grid(row=2, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenfile (Mini)", lambda: open_file_object("Mini")).grid(row=2, column=1, padx=10, pady=8)
    build_button(button_frame, "askopenfiles (Default)", lambda: open_file_objects("Default")).grid(row=3, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenfiles (Mini)", lambda: open_file_objects("Mini")).grid(row=3, column=1, padx=10, pady=8)
    build_button(button_frame, "askdirectory (Default)", lambda: select_directory("Default")).grid(row=4, column=0, padx=10, pady=8)
    build_button(button_frame, "askdirectory (Mini)", lambda: select_directory("Mini")).grid(row=4, column=1, padx=10, pady=8)
    build_button(button_frame, "askopendirname (Default)", lambda: select_directory_name("Default")).grid(row=5, column=0, padx=10, pady=8)
    build_button(button_frame, "askopendirname (Mini)", lambda: select_directory_name("Mini")).grid(row=5, column=1, padx=10, pady=8)
    build_button(button_frame, "askopendirnames (Default)", lambda: select_directory_names("Default")).grid(row=6, column=0, padx=10, pady=8)
    build_button(button_frame, "askopendirnames (Mini)", lambda: select_directory_names("Mini")).grid(row=6, column=1, padx=10, pady=8)
    build_button(button_frame, "askopenpathname (Default)", lambda: open_path_name("Default")).grid(row=7, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenpathname (Mini)", lambda: open_path_name("Mini")).grid(row=7, column=1, padx=10, pady=8)
    build_button(button_frame, "askopenpathnames (Default)", lambda: open_path_names("Default")).grid(row=8, column=0, padx=10, pady=8)
    build_button(button_frame, "askopenpathnames (Mini)", lambda: open_path_names("Mini")).grid(row=8, column=1, padx=10, pady=8)
    build_button(button_frame, "asksaveasfilename (Default)", lambda: save_filename("Default")).grid(row=9, column=0, padx=10, pady=8)
    build_button(button_frame, "asksaveasfilename (Mini)", lambda: save_filename("Mini")).grid(row=9, column=1, padx=10, pady=8)
    build_button(button_frame, "asksaveasfile (Default)", lambda: save_file_object("Default")).grid(row=10, column=0, padx=10, pady=8)
    build_button(button_frame, "asksaveasfile (Mini)", lambda: save_file_object("Mini")).grid(row=10, column=1, padx=10, pady=8)

    theme_switch_frame = ctk.CTkFrame(master=container)
    theme_switch_frame.pack(pady=(10, 0), fill="x")
    theme_switch_frame.grid_columnconfigure(0, weight=1)

    global theme_switch
    theme_switch = ctk.CTkSwitch(master=theme_switch_frame, text="Dark Mode", command=toggle_theme)
    theme_switch.select()
    theme_switch.grid(row=0, column=0, padx=10, pady=8, sticky="w")

    global result_label
    result_label = ctk.CTkLabel(
        master=container,
        text="Result output will appear here",
        wraplength=760,
        justify="left",
        anchor="w"
    )
    result_label.pack(padx=10, pady=(20, 10), fill="x")

    app.mainloop()


if __name__ == "__main__":
    main()

