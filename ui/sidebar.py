import customtkinter as ctk
from PIL import Image, ImageTk

class SideBar:
    def __init__(self, parent):
        self.sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # Add buttons to the sidebar
        self.buttons = []
        for i in range(5):
            button = ctk.CTkButton(self.sidebar_frame, text=f"Button {i+1}", corner_radius=0)
            button.grid(row=i, column=0, padx=20, pady=10)
            self.buttons.append(button)

    def add_button(self, text, command):
        button = ctk.CTkButton(self.sidebar_frame, text=text, command=command)
        button.pack(padx=20, pady=10)
        return button