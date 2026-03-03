#!/usr/bin/env python
"""
Test script to verify asksaveasfilename functionality
"""
import customtkinter as ctk
import CTkFileDialog
import os

def test_save_as_default():
    """Test asksaveasfilename with Default style"""
    print("Opening Default style save dialog...")
    file_path = CTkFileDialog.asksaveasfilename(
        style='Default',
        initial_dir=os.path.expanduser('~'),
        title='Save File (Default Style)',
        geometry=('1320x720', '500x400')
    )
    if file_path:
        print(f"✓ Selected path (Default): {file_path}")
        return True
    else:
        print("✗ No file selected (Default)")
        return False

def test_save_as_mini():
    """Test asksaveasfilename with Mini style"""
    print("Opening Mini style save dialog...")
    file_path = CTkFileDialog.asksaveasfilename(
        style='Mini',
        initial_dir=os.path.expanduser('~'),
        title='Save File (Mini Style)',
        geometry=('1320x720', '500x400')
    )
    if file_path:
        print(f"✓ Selected path (Mini): {file_path}")
        return True
    else:
        print("✗ No file selected (Mini)")
        return False

def test_save_as_file_default():
    """Test asksaveasfile with Default style"""
    print("Opening asksaveasfile dialog (Default)...")
    with CTkFileDialog.asksaveasfile(
        style='Default',
        initial_dir=os.path.expanduser('~'),
        title='Save File with Open (Default)',
        geometry=('1320x720', '500x400')
    ) as f:
        if f:
            print(f"✓ File opened for writing: {f.name}")
            f.write("Test content\n")
            return True
        else:
            print("✗ No file selected for writing (Default)")
            return False

def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    app = ctk.CTk()
    app.geometry("600x400")
    app.title("Save As Functionality Test")

    # Title
    title_label = ctk.CTkLabel(
        app,
        text="Save As Functionality Tests",
        font=("Arial", 18, "bold")
    )
    title_label.pack(pady=20)

    # Test Default Style
    def run_default_test():
        result = test_save_as_default()
        status_label.configure(
            text=f"Default test: {'✓ PASSED' if result else '✗ FAILED'}",
            text_color="green" if result else "red"
        )

    btn_default = ctk.CTkButton(
        app,
        text="Test Default Style",
        command=run_default_test
    )
    btn_default.pack(pady=10)

    # Test Mini Style
    def run_mini_test():
        result = test_save_as_mini()
        status_label.configure(
            text=f"Mini test: {'✓ PASSED' if result else '✗ FAILED'}",
            text_color="green" if result else "red"
        )

    btn_mini = ctk.CTkButton(
        app,
        text="Test Mini Style",
        command=run_mini_test
    )
    btn_mini.pack(pady=10)

    # Test Save As File
    def run_save_file_test():
        result = test_save_as_file_default()
        status_label.configure(
            text=f"Save file test: {'✓ PASSED' if result else '✗ FAILED'}",
            text_color="green" if result else "red"
        )

    btn_save_file = ctk.CTkButton(
        app,
        text="Test Save As File (Default)",
        command=run_save_file_test
    )
    btn_save_file.pack(pady=10)

    # Status label
    status_label = ctk.CTkLabel(
        app,
        text="Select a test to run",
        text_color="gray"
    )
    status_label.pack(pady=20)

    # Exit button
    btn_exit = ctk.CTkButton(
        app,
        text="Exit",
        command=app.quit
    )
    btn_exit.pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    main()
