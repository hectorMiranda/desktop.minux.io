import customtkinter as ctk
from PIL import Image
import os

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, on_action=None):
        super().__init__(parent, fg_color="#1e1e1e")
        self.on_action = on_action or (lambda x: None)
        
        # Create main container with some padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=40, pady=20)
        
        # Title section
        self.create_title_section()
        
        # Create two-column layout
        self.columns_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.columns_frame.pack(expand=True, fill="both", pady=(20, 0))
        
        # Left column (Quick Start)
        self.left_column = ctk.CTkFrame(self.columns_frame, fg_color="transparent")
        self.left_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.create_quick_start_section()
        
        # Right column (Recent)
        self.right_column = ctk.CTkFrame(self.columns_frame, fg_color="transparent")
        self.right_column.pack(side="right", fill="both", expand=True, padx=(20, 0))
        self.create_recent_section()

    def create_title_section(self):
        # Title container
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(fill="x")
        
        try:
            # Load and display app logo
            logo = ctk.CTkImage(
                light_image=Image.open("media/images/logo.png"),
                dark_image=Image.open("media/images/logo.png"),
                size=(64, 64)
            )
            logo_label = ctk.CTkLabel(title_frame, image=logo, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Welcome text
        title = ctk.CTkLabel(
            title_frame,
            text="Welcome to Minux",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(10, 0))
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Your Modern Development Environment",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle.pack()

    def create_quick_start_section(self):
        # Section title
        title = ctk.CTkLabel(
            self.left_column,
            text="Quick Start",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6F6F6F"
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Quick actions
        actions = [
            ("New File", "Create a new file", "file"),
            ("Open Folder", "Open a folder to start working", "folder"),
            ("Clone Git Repository", "Clone a repository from GitHub", "git"),
            ("Open Terminal", "Open integrated terminal", "debug")
        ]
        
        for action, desc, icon_name in actions:
            self.create_action_button(self.left_column, action, desc, icon_name)
            
        # Additional section for learn
        learn_title = ctk.CTkLabel(
            self.left_column,
            text="Learn",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6F6F6F"
        )
        learn_title.pack(anchor="w", pady=(20, 10))
        
        learn_actions = [
            ("Get Started", "A quick tour of Minux features", "help"),
            ("Documentation", "Read the official documentation", "notes"),
            ("Tips and Tricks", "Learn useful tips and shortcuts", "search")
        ]
        
        for action, desc, icon_name in learn_actions:
            self.create_action_button(self.left_column, action, desc, icon_name)

    def create_recent_section(self):
        # Section title
        title = ctk.CTkLabel(
            self.right_column,
            text="Recent",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6F6F6F"
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Recent files/folders frame with scroll
        recent_frame = ctk.CTkScrollableFrame(
            self.right_column,
            fg_color="transparent",
            corner_radius=0
        )
        recent_frame.pack(fill="both", expand=True)
        
        # Sample recent items (in real implementation, these would come from saved settings)
        recent_items = [
            ("~/Documents/Project1", "folder"),
            ("~/Documents/notes.txt", "file"),
            ("~/Projects/website", "folder"),
            ("~/Downloads/script.py", "file")
        ]
        
        for path, item_type in recent_items:
            self.create_recent_item(recent_frame, path, item_type)

    def create_action_button(self, parent, title, description, icon_name):
        # Create container frame for the action
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        frame.pack(fill="x", pady=(0, 5))
        frame.pack_propagate(False)
        
        try:
            # Try to load icon
            icon = ctk.CTkImage(
                light_image=Image.open(f"media/icons/{icon_name}.png"),
                dark_image=Image.open(f"media/icons/{icon_name}.png"),
                size=(16, 16)
            )
        except:
            icon = None
        
        # Create button
        btn = ctk.CTkButton(
            frame,
            text=f"{title}\n{description}",
            font=ctk.CTkFont(size=13),
            image=icon,
            anchor="w",
            fg_color="transparent",
            hover_color="gray20",
            compound="left",
            height=40,
            corner_radius=0,
            command=lambda t=title: self.on_action(t)
        )
        btn.pack(fill="x")

    def create_recent_item(self, parent, path, item_type):
        try:
            # Try to load icon
            icon = ctk.CTkImage(
                light_image=Image.open(f"media/icons/{item_type}.png"),
                dark_image=Image.open(f"media/icons/{item_type}.png"),
                size=(16, 16)
            )
        except:
            icon = None
        
        # Create button for the recent item
        btn = ctk.CTkButton(
            parent,
            text=os.path.basename(path),
            font=ctk.CTkFont(size=13),
            image=icon,
            anchor="w",
            fg_color="transparent",
            hover_color="gray20",
            compound="left",
            height=30,
            corner_radius=0,
            command=lambda p=path: self.on_action(("open", p))
        )
        btn.pack(fill="x", pady=(0, 2))
        
        # Add path label
        path_label = ctk.CTkLabel(
            parent,
            text=os.path.dirname(path),
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="w"
        )
        path_label.pack(fill="x", padx=(30, 0), pady=(0, 5))
