import customtkinter as ctk
from PIL import Image
import os
import sqlite3
from datetime import datetime
import tempfile

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=0)
        self.callback = callback
        self.app = parent  # Store reference to main app
        
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
        """Create a clickable action button with icon and description"""
        # Create main frame for the button
        button_frame = ctk.CTkFrame(parent, fg_color="#2D2D2D", corner_radius=4)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Create content frame
        content = ctk.CTkFrame(button_frame, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=10)
        
        try:
            # Get the absolute path to the icons directory
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media", "icons", icon_name)
            icon = ctk.CTkImage(
                light_image=Image.open(icon_path),
                dark_image=Image.open(icon_path),
                size=(16, 16)
            )
            icon_label = ctk.CTkLabel(
                content,
                text="",
                image=icon,
                width=20,
                cursor="hand2"
            )
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            icon_label = ctk.CTkLabel(
                content,
                text="📁",
                font=ctk.CTkFont(size=14),
                width=20,
                text_color="#858585",
                cursor="hand2"
            )
        icon_label.pack(side="left", padx=(0, 5))
        
        # Add title
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#CCCCCC",
            cursor="hand2"
        )
        title_label.pack(side="left")
        
        # Add description
        if description:
            desc_label = ctk.CTkLabel(
                content,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color="#858585",
                cursor="hand2"
            )
            desc_label.pack(side="left", padx=(5, 0))
        
        # Set cursor for frames
        button_frame.configure(cursor="hand2")
        content.configure(cursor="hand2")
        
        # Add hover effect and click handling
        def on_enter(e):
            button_frame.configure(fg_color="#404040")
        
        def on_leave(e):
            button_frame.configure(fg_color="#2D2D2D")
        
        def on_click(e):
            if title == "Open Folder":
                self.open_folder_dialog()
        
        # Bind events to all widgets in the button
        for widget in [button_frame, content, icon_label, title_label] + ([desc_label] if description else []):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
        
        return button_frame

    def open_folder_dialog(self):
        """Open a folder dialog and launch a new window with the selected folder as working directory"""
        import tkinter.filedialog as filedialog
        import subprocess
        import sys
        import os
        import tempfile
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Select Folder",
            initialdir=os.path.expanduser("~")  # Start from user's home directory
        )
        
        if folder_path:
            # Get the path to the app directory
            app_dir = os.path.dirname(os.path.dirname(__file__))  # Parent directory of ui/
            
            # Create a temporary wrapper script that sets up the Python path
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f'''import os, sys

# Get the absolute path to the app directory
app_dir = {repr(app_dir)}

# Change to app directory first
os.chdir(app_dir)

# Add app directory to Python path
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Now we can import the app
from ui.app import App

if __name__ == '__main__':
    # Get the target folder from command line args
    target_folder = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run the app
    app = App(target_folder)
    app.mainloop()
''')
                wrapper_path = f.name
            
            # Launch new window using the wrapper script
            try:
                subprocess.Popen(
                    [sys.executable, wrapper_path, folder_path],
                    cwd=app_dir  # Start from app directory
                )
                
                # Schedule wrapper script cleanup
                def cleanup():
                    try:
                        if os.path.exists(wrapper_path):
                            os.unlink(wrapper_path)
                    except:
                        pass
                
                self.after(1000, cleanup)  # Clean up after 1 second
                
                # Close current window if it's not the main window
                if hasattr(self.app, 'quit'):
                    self.app.quit()
            except Exception as e:
                if hasattr(self.app, 'show_error_notification'):
                    self.app.show_error_notification(f"Error opening folder: {e}")
                else:
                    print(f"Error opening folder: {e}")
                # Clean up wrapper script on error
                try:
                    os.unlink(wrapper_path)
                except:
                    pass

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
