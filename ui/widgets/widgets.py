import customtkinter as ctk
from PIL import Image, ImageTk

class StatusBar:
    def __init__(self, parent, icon_size):
        self.status_bar_frame = ctk.CTkFrame(parent, height=icon_size[0], fg_color="gray", corner_radius=0)
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.status_bar_frame.grid_columnconfigure(1, weight=1)
        self.status_bar_frame.grid_propagate(False)

        self.power_image = ctk.CTkImage(Image.open("./media/icons/power.png").resize(icon_size))
        self.settings_image = ctk.CTkImage(Image.open("./media/icons/settings.png").resize(icon_size))

        self.power_button = ctk.CTkButton(self.status_bar_frame, image=self.power_image, text="", fg_color="gray", hover_color="red", corner_radius=0, width=icon_size[0], height=icon_size[1])
        self.power_button.grid(row=0, column=0, padx=1, pady=1)
        self.settings_button = ctk.CTkButton(self.status_bar_frame, image=self.settings_image, text="", fg_color="gray", hover_color="orange", corner_radius=0, width=100)
        self.settings_button.grid(row=0, column=2, padx=1, sticky="w")

    def update_time(self, time_label):
        self.status_bar_label = ctk.CTkLabel(self.status_bar_frame, text=time_label)
        self.status_bar_label.grid(row=0, column=3, padx=1, sticky="e")

class SideBar:
    def __init__(self, parent):
        self.sidebar_frame = ctk.CTkFrame(parent, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

    def add_button(self, text, command):
        button = ctk.CTkButton(self.sidebar_frame, text=text, command=command)
        button.pack(padx=20, pady=10)
        return button
