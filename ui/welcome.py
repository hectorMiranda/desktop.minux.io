import customtkinter as ctk
from PIL import Image
import os
import sqlite3
from datetime import datetime

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=0)
        self.callback = callback
        
        # Create main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title section
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 40))
        
        # Load and display logo
        logo_path = os.path.join("media", "images", "logo.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                if logo_image.mode != 'RGBA':
                    logo_image = logo_image.convert('RGBA')
                logo_img = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(64, 64))
                logo_label = ctk.CTkLabel(title_frame, image=logo_img, text="")
                logo_label.pack(side="left")
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Title and description
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left", padx=20)
        
        title = ctk.CTkLabel(
            text_frame,
            text="Welcome to Minux",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CCCCCC"
        )
        title.pack(anchor="w")
        
        description = ctk.CTkLabel(
            text_frame,
            text="Your all-in-one development environment",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        description.pack(anchor="w")
        
        # Create two-column layout
        columns_frame = ctk.CTkFrame(container, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        
        # Left column - Quick Start
        left_column = ctk.CTkFrame(columns_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        quick_start_label = ctk.CTkLabel(
            left_column,
            text="Quick Start",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#CCCCCC"
        )
        quick_start_label.pack(anchor="w", pady=(0, 10))
        
        # Quick Start buttons
        self.create_action_button(left_column, "New File", "file.png", "Create a new file")
        self.create_action_button(left_column, "Open Folder", "folder.png", "Open a folder")
        self.create_action_button(left_column, "Clone Git Repository", "git.png", "Clone from Git")
        self.create_action_button(left_column, "Open Terminal", "debug.png", "Open integrated terminal")
        
        # Right column - Pending Tasks
        right_column = ctk.CTkFrame(columns_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True)
        
        pending_tasks_label = ctk.CTkLabel(
            right_column,
            text="Pending Tasks",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#CCCCCC"
        )
        pending_tasks_label.pack(anchor="w", pady=(0, 10))
        
        # Create scrollable frame for tasks
        tasks_frame = ctk.CTkScrollableFrame(right_column, fg_color="transparent", corner_radius=0)
        tasks_frame.pack(fill="both", expand=True)
        
        # Load and display pending tasks
        self.load_pending_tasks(tasks_frame)

    def create_action_button(self, parent, title, icon_name, description):
        """Create a button with icon and description"""
        btn_frame = ctk.CTkFrame(parent, fg_color="#2a2d2e", corner_radius=5)
        btn_frame.pack(fill="x", pady=5)
        btn_frame.bind("<Button-1>", lambda e: self.callback(title))
        
        content_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Try to load icon
        icon_path = os.path.join("media", "icons", icon_name)
        if os.path.exists(icon_path):
            try:
                icon_image = Image.open(icon_path)
                if icon_image.mode != 'RGBA':
                    icon_image = icon_image.convert('RGBA')
                icon_img = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(24, 24))
                icon_label = ctk.CTkLabel(content_frame, image=icon_img, text="")
                icon_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Error loading icon {icon_name}: {e}")
        
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CCCCCC",
            anchor="w"
        )
        title_label.pack(fill="x")
        
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="w"
        )
        desc_label.pack(fill="x")

    def load_pending_tasks(self, container):
        """Load and display pending tasks from SQLite database"""
        try:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'minux.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get pending (not done) tasks, ordered by creation date
            cursor.execute('''
                SELECT task, created_date 
                FROM todos 
                WHERE done = 0 
                ORDER BY created_date DESC 
                LIMIT 5
            ''')
            
            tasks = cursor.fetchall()
            conn.close()
            
            if not tasks:
                # Show message when no tasks are pending
                no_tasks_label = ctk.CTkLabel(
                    container,
                    text="No pending tasks",
                    font=ctk.CTkFont(size=12),
                    text_color="#888888"
                )
                no_tasks_label.pack(pady=10)
                return
            
            # Create a task button for each pending task
            for task, created_date in tasks:
                self.create_task_button(container, task, created_date)
                
        except Exception as e:
            # Show error message if database access fails
            error_label = ctk.CTkLabel(
                container,
                text=f"Could not load tasks: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="#ff6b6b"
            )
            error_label.pack(pady=10)

    def create_task_button(self, parent, task, created_date):
        """Create a button for a pending task"""
        btn_frame = ctk.CTkFrame(parent, fg_color="#2a2d2e", corner_radius=5)
        btn_frame.pack(fill="x", pady=5)
        
        # Make the entire frame clickable
        btn_frame.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
        btn_frame.bind("<Enter>", lambda e: btn_frame.configure(fg_color="#404040"))
        btn_frame.bind("<Leave>", lambda e: btn_frame.configure(fg_color="#2a2d2e"))
        
        content_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)
        content_frame.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
        
        # Try to load todo icon
        icon_path = os.path.join("media", "icons", "todo.png")
        if os.path.exists(icon_path):
            try:
                icon_image = Image.open(icon_path)
                if icon_image.mode != 'RGBA':
                    icon_image = icon_image.convert('RGBA')
                icon_img = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(24, 24))
                icon_label = ctk.CTkLabel(content_frame, image=icon_img, text="")
                icon_label.pack(side="left", padx=(0, 10))
                # Make icon label clickable too
                icon_label.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
            except Exception as e:
                print(f"Error loading todo icon: {e}")
        
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        text_frame.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
        
        # Show task text
        task_label = ctk.CTkLabel(
            text_frame,
            text=task,
            font=ctk.CTkFont(size=14),
            text_color="#CCCCCC",
            anchor="w"
        )
        task_label.pack(fill="x")
        task_label.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
        
        # Show creation date
        try:
            date_obj = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
            date_str = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            date_str = created_date
            
        date_label = ctk.CTkLabel(
            text_frame,
            text=f"Created: {date_str}",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="w"
        )
        date_label.pack(fill="x")
        date_label.bind("<Button-1>", lambda e: self.callback(("open_todo", task)))
        
        # Change cursor to hand when hovering over any part of the button
        for widget in [btn_frame, content_frame, text_frame, task_label, date_label]:
            widget.bind("<Enter>", lambda e: widget.configure(cursor="hand2"))
            widget.bind("<Leave>", lambda e: widget.configure(cursor=""))
