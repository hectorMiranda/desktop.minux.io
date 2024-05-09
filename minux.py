import os
import customtkinter as ctk
import platform
import datetime
from PIL import Image, ImageTk
import logging
import configparser
import json
from ui.status_bar import StatusBar
from ui.sidebar import SideBar
from ui.widgets.common import Clock, Timer, StopWatch, Alarm, Doge


ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")  

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', filename='navigator.log', filemode='a')

SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', 'service_account_key.json')

class App(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.title("Minux")
        self.geometry("1100x580")

        icon_size = (50, 50)
        logging.info(platform.system())
        
        if platform.system() == "Windows":
            self.state("zoomed")
        elif platform.system() == "Darwin": 
            #self.attributes("-fullscreen", True)
            print("Darwin")
        else:
            self.attributes('-zoomed', True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=0)
        
        self.config = configparser.ConfigParser()
        self.config.read('configs/minux.ini') 
        self.logo_path = self.config.get('images', 'logo')  
        self.logo_image = Image.open(self.logo_path).resize((106, 95))         
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="Logo label")
        logo_label.pack(pady=10)  
        self.sidebar_dashboard_button = ctk.CTkButton(self.sidebar_frame, command=self.show_dashboard, text="Dashboard")
        self.sidebar_dashboard_button.pack(padx=30, pady=30)
        self.add_tab_button = ctk.CTkButton(self.sidebar_frame, text="Media", command=self.show_add_widget_dialog)
        self.add_tab_button.pack(padx=20, pady=10)
        self.power_image = ctk.CTkImage(Image.open("./media/icons/power.png").resize(icon_size))
        self.settings_image = ctk.CTkImage(Image.open("./media/icons/settings.png").resize(icon_size))
        
        self.status_bar = StatusBar(self, icon_size)
        self.sidebar = SideBar(self)

        self.sidebar.add_button("Dashboard", self.show_dashboard)
        self.sidebar.add_button("Media", self.show_add_widget_dialog)
        self.sidebar.add_button("Music Companion", self.show_music_companion)
        self.sidebar.add_button("Vault", self.show_vault_panel)
        self.sidebar.add_button("Conversation", self.show_conversation)
        self.sidebar.add_button("Data Science", self.show_dashboard)
        
        self.status_bar_frame = ctk.CTkFrame(self, height=icon_size[0], fg_color="gray", corner_radius=0)
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.status_bar_frame.grid_columnconfigure(1, weight=1)
        self.status_bar_frame.grid_propagate(False)
        
        
        self.status_bar_label = ctk.CTkLabel(self.status_bar_frame, text="")
        self.status_bar_label.grid(row=0, column=3, padx=1, sticky="e")
        self.update_time()
    
        
        self.sidebar_music_companion_button = ctk.CTkButton(self.sidebar_frame, command=self.show_music_companion, text="Music companion")
        self.sidebar_music_companion_button.pack(padx=20, pady=10)
        self.sidebar_vault_button = ctk.CTkButton(self.sidebar_frame, command=self.show_vault_panel, text="Vault")
        self.sidebar_vault_button.pack(padx=20, pady=10)
        self.sidebar_conversation_button = ctk.CTkButton(self.sidebar_frame, command=self.show_conversation, text="Conversation")
        self.sidebar_conversation_button.pack(padx=20, pady=10)
        self.sidebar_data_science_button = ctk.CTkButton(self.sidebar_frame, command=self.show_conversation, text="Data Science")
        self.sidebar_data_science_button.pack(padx=20, pady=10)


        # Main Content Panels
        self.panel1 = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.panel2 = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.panel3 = ctk.CTkFrame(self, width=250, corner_radius=0)

        # Status Bar Buttons for Panel Switching
        self.power_button = ctk.CTkButton(self.status_bar_frame, image=self.power_image, command=self.quit_app, width=icon_size[0], height=icon_size[1], fg_color="gray", text="", hover_color="red", corner_radius=0)

        self.power_button.grid(row=0, column=0, padx=1, pady=1)
        self.status_button_2 = ctk.CTkButton(self.status_bar_frame, text="Conversation", command=self.show_conversation, height=icon_size[1], corner_radius=0, hover_color="black")
        self.status_button_2.grid(row=0, column=1, padx=3, sticky="w")
        self.settings_button = ctk.CTkButton(self.status_bar_frame, text="", image=self.settings_image, command=self.show_settings, fg_color="gray", hover_color="orange", corner_radius=0, width=100)
        self.settings_button.grid(row=0, column=2, padx=1, sticky="w")
        
        self.widgets = []

        self.show_dashboard()
        
    def show_add_widget_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Media")
        dialog.geometry("300x200")

        todo_button = ctk.CTkButton(dialog, text="TODO Widget", command=lambda: self.add_widget("TODO"))
        todo_button.pack(pady=10)

        voice_button = ctk.CTkButton(dialog, text="Voice Recorder Widget", command=lambda: self.add_widget("Voice"))
        voice_button.pack(pady=10)

    def add_widget(self, widget_type):
        widget = None
        if widget_type == "TODO":
            widget = ctk.CTkLabel(self.panel1, text="TODO Widget")
        elif widget_type == "Voice":
            widget = ctk.CTkLabel(self.panel1, text="Voice Recorder Widget")
        widget.pack()
        self.widgets.append({"type": widget_type, "widget": widget})
        self.save_widgets()

    def save_widgets(self):
        with open('widgets.json', 'w') as f:
            json.dump([w['type'] for w in self.widgets], f)

    def load_widgets(self):
        self.widgets = []
        if os.path.exists('widgets.json'):
            with open('widgets.json', 'r') as f:
                widget_types = json.load(f)
                for widget_type in widget_types:
                    self.add_widget(widget_type)
                    
                    
    def save_transparency(transparency):
        with open('settings.txt', 'w') as file:
            file.write(str(transparency))
        
    def load_transparency():
        try:
            with open('settings.txt', 'r') as file:
                return float(file.read())
        except (FileNotFoundError, ValueError):
            return 1.0  # Default transparency

    def update_transparency(value):
        transparency = float(value)
        root.attributes('-alpha', transparency)
        save_transparency(transparency)
        
    def quit_app(self):
        confirmation_dialog = ctk.CTkToplevel(self)
        confirmation_dialog.title("Exit Confirmation")

        # Make the window modal
        confirmation_dialog.transient(self)
        confirmation_dialog.grab_set()

        # Set window size and disable resizing
        confirmation_dialog.geometry("300x300")
        confirmation_dialog.resizable(False, False)

        # Center the dialog on the screen
        # Calculate position x, y
        x = self.winfo_x() + self.winfo_width() // 2 - 150
        y = self.winfo_y() + self.winfo_height() // 2 - 100
        confirmation_dialog.geometry("+%d+%d" % (x, y))



        logo_label = ctk.CTkLabel(confirmation_dialog, image=self.logo_image, text="")
        logo_label.pack(pady=10)  
        confirmation_label = ctk.CTkLabel(confirmation_dialog, text="Are you sure you want to exit?")
        confirmation_label.pack(pady=0)

    

        yes_button = ctk.CTkButton(confirmation_dialog, text="Yes", command=lambda: [confirmation_dialog.destroy(), self.quit()])
        no_button = ctk.CTkButton(confirmation_dialog, text="No", command=confirmation_dialog.destroy)
        
        yes_button.pack(side='left', fill='x', expand=True, padx=20, pady=0)
        no_button.pack(side='right', fill='x', expand=True, padx=20, pady=0)

        self.wait_window(confirmation_dialog)



    def new_tab(self):
        confirmation_dialog = ctk.CTkToplevel(self)
        confirmation_dialog.title("Exit Confirmation")
        dialog_width = 400
        dialog_height = 150
        confirmation_dialog.geometry(f"{dialog_width}x{dialog_height}")


        screen_width = confirmation_dialog.winfo_screenwidth()
        screen_height = confirmation_dialog.winfo_screenheight()
        center_x = int(screen_width / 2 - dialog_width / 2)
        center_y = int(screen_height / 2 - dialog_height / 2)
        confirmation_dialog.geometry(f"+{center_x}+{center_y}")

        # Customized label layout without the image, with better font and padding
        confirmation_label = ctk.CTkLabel(confirmation_dialog, text="Are you sure you want to exit?",
                                        font=ctk.CTkFont(size=12), fg_color=None, text_color="black")
        confirmation_label.pack(pady=20, padx=20)

        # Frame for buttons with padding
        button_frame = ctk.CTkFrame(confirmation_dialog)
        button_frame.pack(fill='x', expand=True, pady=10)

        # Stylish buttons with custom colors and padding
        yes_button = ctk.CTkButton(button_frame, text="Yes", command=self.quit,
                                    fg_color="green", hover_color="light green")
        no_button = ctk.CTkButton(button_frame, text="No", command=confirmation_dialog.destroy,
                                fg_color="red", hover_color="light coral")
        
        yes_button.pack(side='left', fill='x', expand=True, padx=10)
        no_button.pack(side='right', fill='x', expand=True, padx=10)

        
    def show_settings(self):
        if not hasattr(self, 'settings_frame'):
            self.settings_frame = ctk.CTkFrame(self, width=400, height=300, corner_radius=10)
            self.settings_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
            
            appearance_mode_label = ctk.CTkLabel(self.settings_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.pack(padx=20, pady=(10, 0))
            appearance_mode_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
            appearance_mode_optionmenu.pack(padx=20, pady=(0, 10))

            scaling_label = ctk.CTkLabel(self.settings_frame, text="UI Scaling:", anchor="w")
            scaling_label.pack(padx=20, pady=(10, 0))
            scaling_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
            scaling_optionmenu.pack(padx=20, pady=(0, 10))

            close_button = ctk.CTkButton(self.settings_frame, text="Close", command=self.close_settings)
            close_button.pack(pady=20)

        self.settings_frame.lift()

    def close_settings(self):
        if hasattr(self, 'settings_frame'):
            self.settings_frame.destroy()
            del self.settings_frame 


    def update_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        self.status_bar_label.configure(text=f"{current_time} \n {current_date} ", padx=10, pady=10, font=ctk.CTkFont(size=12), text_color="white")
        self.after(1000, self.update_time)
        
    def show_dashboard(self):
        
        self.clear_panels()
        label = ctk.CTkLabel(self.panel1, text="Dashboard", anchor="w", padx=20, font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")

        # Example widgets for the dashboard
        # Widget 1: System Status
        status_label = ctk.CTkLabel(self.panel1, text="System Status:", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        status_label.grid(row=1, column=0, pady=(10, 0), sticky="w")
        status_value = ctk.CTkLabel(self.panel1, text="Online", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        status_value.grid(row=1, column=1, pady=(10, 0), sticky="w")

        # Widget 2: CPU Usage
        cpu_label = ctk.CTkLabel(self.panel1, text="CPU Usage:", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        cpu_label.grid(row=2, column=0, pady=(10, 0), sticky="w")
        cpu_value = ctk.CTkLabel(self.panel1, text="45%", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        cpu_value.grid(row=2, column=1, pady=(10, 0), sticky="w")

        # Widget 3: Memory Usage
        memory_label = ctk.CTkLabel(self.panel1, text="Memory Usage:", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        memory_label.grid(row=3, column=0, pady=(10, 0), sticky="w")
        memory_value = ctk.CTkLabel(self.panel1, text="32%", anchor="w", padx=20, font=ctk.CTkFont(size=14))
        memory_value.grid(row=3, column=1, pady=(10, 0), sticky="w")

        # Ensure all labels are in the first column, values in the second
        self.panel1.grid_columnconfigure(0, weight=1)
        self.panel1.grid_columnconfigure(1, weight=1)

        # Display the panel after setting it up
        self.panel1.grid(row=0, column=1, rowspan=3, sticky="nsew")


    def show_conversation(self):
        self.clear_panels()

        # Set the panel layout to fill the available space
        self.panel1.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.panel1.grid_rowconfigure(1, weight=1)
        self.panel1.grid_columnconfigure(0, weight=1)
        
        # Create the Panel 1 specific widgets
        label = ctk.CTkLabel(self.panel1, text="Welcome to the conversation", anchor="w", padx=20, font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(10, 10), sticky="nsew")

        # Chat history area with a modern look
        self.chat_history = ctk.CTkTextbox(self.panel1, height=15, corner_radius=10, fg_color="#2e2e2e", text_color="white")
        self.chat_history.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Frame for the user input and send button
        input_frame = ctk.CTkFrame(self.panel1, corner_radius=0)
        input_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        # User input entry
        self.user_input = ctk.CTkEntry(input_frame, placeholder_text="Ask me anything...", corner_radius=10)
        self.user_input.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        # Send button with a modern look
        send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message, corner_radius=10, fg_color="#4a7dfc", hover_color="#5a8ffc")
        send_button.grid(row=0, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew")


        
    def send_message(self):
        user_message = self.user_input.get()
        if user_message.strip() != "":
            # Display the user's message in the chat history
            self.chat_history.insert("end", f"You: {user_message}\n")
            self.chat_history.see("end")

            # Clear the user input entry
            self.user_input.delete(0, "end")

            # Here, you can add the code to call the OpenAI API and get a response
            # For demonstration purposes, we'll just echo the user's message
            bot_response = f"Bot: {user_message}\n"

            # Display the bot's response in the chat history
            self.chat_history.insert("end", bot_response)
            self.chat_history.see("end")



    def show_music_companion(self):
        self.clear_panels()
        label = ctk.CTkLabel(self.panel2, text="Music companion", anchor="w", padx=20, font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        
        # Display the panel after setting it up
        self.panel2.grid(row=0, column=1, rowspan=3, sticky="nsew")

        

    def show_vault_panel(self):
        self.clear_panels()
        label = ctk.CTkLabel(self.panel3, text="Vault", anchor="w", padx=20, font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        
        # Display the panel after setting it up
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
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def some_function(self):
        print("Button clicked!")

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"An exception occurred: {e}")
