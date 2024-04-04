import tkinter
import tkinter.messagebox
import customtkinter
from customtkinter import CTkImage 
import platform
import datetime
from PIL import Image, ImageTk
import logging

customtkinter.set_appearance_mode("Dark")  
customtkinter.set_default_color_theme("blue")  

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='navigator.log',
                    filemode='a')


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control Panel")
        self.geometry(f"{1100}x{580}")  
        icon_size = (50, 50)  
        
        logging.info(platform.system())

        
        self.power_image = CTkImage(Image.open("icons/power.png").resize(icon_size))
        self.settings_image = CTkImage(Image.open("icons/settings.png").resize(icon_size))

        # Check for platform and maximize accordingly
        if platform.system() == "Windows":
            self.state("zoomed")
        elif platform.system() == "Darwin":  # Darwin is the system name for macOS
            # Get screen width and height
            ws = self.winfo_screenwidth()  
            hs = self.winfo_screenheight()
            self.geometry(f"{ws}x{hs}+0+0")
        else:
            self.attributes('-zoomed', True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=0)

        # Status Bar
        self.status_bar_frame = customtkinter.CTkFrame(self, height=icon_size[0], fg_color="gray", corner_radius=0)
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.status_bar_frame.grid_columnconfigure(1, weight=1)
        self.status_bar_frame.grid_propagate(False)
        
        # Sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=0)
        
        # Status bar time label
        self.status_bar_label = customtkinter.CTkLabel(self.status_bar_frame, text="")
        self.status_bar_label.grid(row=0, column=3, padx=1, sticky="e")
        self.update_time()

        # Sidebar Buttons
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Marcetux", font=customtkinter.CTkFont(size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_conversation, text="Dashboard")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_panel_2, text="Preferences")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_panel_3, text="Vault")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)


        # Main Content Panels
        self.panel1 = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.panel2 = customtkinter.CTkFrame(self, width=250, corner_radius=0)
        self.panel3 = customtkinter.CTkFrame(self, width=250, corner_radius=0)

        # Status Bar Buttons for Panel Switching
        self.power_button = customtkinter.CTkButton(self.status_bar_frame, image=self.power_image, command=self.quit_app, width=icon_size[0], height=icon_size[1], fg_color="gray", text="", hover_color="red", corner_radius=0)

        self.power_button.grid(row=0, column=0, padx=1, pady=1)
        self.status_button_2 = customtkinter.CTkButton(self.status_bar_frame, text="Conversation", command=self.show_conversation, height=icon_size[1], corner_radius=0, hover_color="black")
        self.status_button_2.grid(row=0, column=1, padx=3, sticky="w")
        self.settings_button = customtkinter.CTkButton(self.status_bar_frame, text="", image=self.settings_image, command=self.show_settings, fg_color="gray", hover_color="orange", corner_radius=0, width=100)
        self.settings_button.grid(row=0, column=2, padx=1, sticky="w")
        
        # Show the first panel by default
        self.show_conversation()
        
    def quit_app(self):
        #save whatever is pending
        self.quit()
        
    def show_settings(self):
        # Create the settings frame only if it does not exist
        if not hasattr(self, 'settings_frame'):
            self.settings_frame = customtkinter.CTkFrame(self, width=400, height=300, corner_radius=10)
            self.settings_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
            
            # Appearance Mode Option
            appearance_mode_label = customtkinter.CTkLabel(self.settings_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.pack(padx=20, pady=(10, 0))
            appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
            appearance_mode_optionmenu.pack(padx=20, pady=(0, 10))

            # UI Scaling Option
            scaling_label = customtkinter.CTkLabel(self.settings_frame, text="UI Scaling:", anchor="w")
            scaling_label.pack(padx=20, pady=(10, 0))
            scaling_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
            scaling_optionmenu.pack(padx=20, pady=(0, 10))

            # Close Button for the settings frame
            close_button = customtkinter.CTkButton(self.settings_frame, text="Close", command=self.close_settings)
            close_button.pack(pady=20)

        # Bring the settings frame to the top
        self.settings_frame.lift()

    def close_settings(self):
        if hasattr(self, 'settings_frame'):
            self.settings_frame.destroy()
            del self.settings_frame 


    def update_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        self.status_bar_label.configure(text=f"{current_time} \n {current_date} ", padx=10, pady=10, font=customtkinter.CTkFont(size=12), text_color="white")
        self.after(1000, self.update_time)

    def show_conversation(self):
        self.clear_panels()
        # Set the panel layout to fill the available space
        self.panel1.grid_rowconfigure(1, weight=1)
        self.panel1.grid_columnconfigure(0, weight=1)

        # Create the Panel 1 specific widgets
        label = customtkinter.CTkLabel(self.panel1, text="Welcome to the conversation", anchor="w", padx=20, font=customtkinter.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(10, 10), sticky="nsew")

        # Chat history area with a modern look
        self.chat_history = customtkinter.CTkTextbox(self.panel1, height=15, corner_radius=10, fg_color="#2e2e2e", text_color="white")
        self.chat_history.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Frame for the user input and send button
        input_frame = customtkinter.CTkFrame(self.panel1, corner_radius=0)
        input_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        # User input entry
        self.user_input = customtkinter.CTkEntry(input_frame, placeholder_text="Ask me anything...", corner_radius=10)
        self.user_input.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        # Send button with a modern look
        send_button = customtkinter.CTkButton(input_frame, text="Send", command=self.send_message, corner_radius=10, fg_color="#4a7dfc", hover_color="#5a8ffc")
        send_button.grid(row=0, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew")

        # Finally, grid the panel itself
        self.panel1.grid(row=0, column=1, rowspan=3, sticky="nsew")

        
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



    def show_panel_2(self):
        self.clear_panels()
        label = customtkinter.CTkLabel(self.panel1, text="This is Panel 2", anchor="w", padx=20)
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        
        
        # Setup widgets for panel 2
        self.panel2.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def show_panel_3(self):
        label = customtkinter.CTkLabel(self.panel1, text="This is Panel 3", anchor="w", padx=20)
        label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        
        
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
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"An exception occurred: {e}")
