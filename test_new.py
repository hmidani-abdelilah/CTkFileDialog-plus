import customtkinter as ctk
from CTkFileDialog import askopenfile

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def open_file_obj():
    f = askopenfile(mode='r', 
                    filetypes=[("Binary","*.bin"), ("All","*.*")])
    if f:
        data = f.read()
        f.close()
        result_label.configure(text=f"Read {len(data)/1024/1024:.2f} MB from {f.name}")

app = ctk.CTk()
app.title("askopenfile Demo")
app.geometry("500x200")

ctk.CTkButton(app, text="Open File Object", command=open_file_obj).pack(pady=20)
result_label = ctk.CTkLabel(app, text="Waiting for file selection...")
result_label.pack()

app.mainloop()