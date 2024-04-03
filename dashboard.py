import tkinter
import tkinter.messagebox
import customtkinter
import platform
import datetime

customtkinter.set_appearance_mode("System")  # System appearance mode
customtkinter.set_default_color_theme("blue")  # Default color theme

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control Panel")
        self.geometry(f"{1100}x{580}")  # Window size

        print(platform.system())

        if platform.system() == "Windows":
            self.state("zoomed")
        else:
            self.attributes("-zoomed", True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=0)

        # Status Bar
        self.status_bar_frame = customtkinter.CTkFrame(self, height=30, fg_color="gray")
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.status_bar_frame.grid_columnconfigure(1, weight=1)
        self.status_bar_frame.grid_propagate(False)
        
        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=0)
        
        # Status bar time label
        self.status_bar_label = customtkinter.CTkLabel(self.status_bar_frame, text="")
        self.status_bar_label.grid(row=0, column=3, padx=10, sticky="e")
        self.update_time()

        # Sidebar Buttons
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Marcetux", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_panel_1, text="Dashboard")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_panel_2, text="Preferences")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_panel_3, text="Vault")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Appearance Mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # UI Scaling
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(5, 0))  # Reduce padding below label
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=8, column=0, padx=20, pady=(0, 5))


        # Main Content Panels
        self.panel1 = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.panel2 = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.panel3 = customtkinter.CTkFrame(self, width=250, corner_radius=0)

        # Status Bar Buttons for Panel Switching
        self.status_button_1 = customtkinter.CTkButton(self.status_bar_frame, text="Panel 1", command=self.show_panel_1)
        self.status_button_1.grid(row=0, column=0, padx=5, sticky="w")
        self.status_button_2 = customtkinter.CTkButton(self.status_bar_frame, text="Panel 2", command=self.show_panel_2)
        self.status_button_2.grid(row=0, column=1, padx=5, sticky="w")
        self.status_button_3 = customtkinter.CTkButton(self.status_bar_frame, text="Panel 3", command=self.show_panel_3)
        self.status_button_3.grid(row=0, column=2, padx=5, sticky="w")
        
        # Show the first panel by default
        self.show_panel_1()

    def update_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        self.status_bar_label.configure(text=f"{current_date} {current_time}")
        self.after(1000, self.update_time)

    def show_panel_1(self):
        self.clear_panels()
        # Now create the Panel 1 specific widgets
        label = customtkinter.CTkLabel(self.panel1, text="This is Panel 1", anchor="w", padx=20)
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")

        entry = customtkinter.CTkEntry(self.panel1, placeholder_text="Enter something...")
        entry.grid(row=1, column=0, padx=20, sticky="ew")

        button = customtkinter.CTkButton(self.panel1, text="Click me", command=self.some_function)
        button.grid(row=2, column=0, padx=20, pady=(10, 20))

        # Finally, grid the panel itself
        self.panel1.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def show_panel_2(self):
        self.clear_panels()
        # Setup widgets for panel 2
        self.panel2.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def show_panel_3(self):
        self.clear_panels()
        # Setup widgets for panel 3
        self.panel3.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def clear_panels(self):
        # This method clears all widgets from the main content area
        for widget in self.panel1.winfo_children():
            widget.destroy()
        for widget in self.panel2.winfo_children():
            widget.destroy()
        for widget in self.panel3.winfo_children():
            widget.destroy()

        self.panel1.grid_remove()
        self.panel2.grid_remove()
        self.panel3.grid_remove()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def some_function(self):
        print("Button clicked!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
