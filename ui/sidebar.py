import customtkinter as ctk
from PIL import Image, ImageTk

class SideBar:
    def __init__(self, parent):
        self.sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

    def add_button(self, text, command):
        button = ctk.CTkButton(self.sidebar_frame, text=text, command=command)
        button.pack(padx=20, pady=10)
        return button