import os
import customtkinter as ctk
import platform
import datetime
from PIL import Image, ImageTk
import logging
import logging.handlers
import configparser
import json
from ui.status_bar import StatusBar
from ui.sidebar import SideBar
from ui.widgets.common import Clock, Timer, StopWatch, Alarm, Doge
from handlers.FilteredStreamHandler import FilteredStreamHandler
import fitz 
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import queue
from ui.explorer import FileExplorer
from ui.tabs import TabView
from ui.file_viewer import FileViewer
from ui.widgets.todo import TodoWidget
from ui.welcome import WelcomeScreen
import sqlite3
import threading
from pathlib import Path


# Set dark mode as default
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# Configure logging to write to a queue
log_queue = queue.Queue()
queue_handler = logging.handlers.QueueHandler(log_queue)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('navigator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the logger for this module
logger = logging.getLogger(__name__)
# Add queue handler to the logger
logger.addHandler(queue_handler)

os.environ["PYTHONWARNINGS"] = "ignore:ApplePersistenceIgnoreState"





SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', 'service_account_key.json')

class TerminalHandler(logging.Handler):
    def __init__(self, terminal):
        super().__init__()
        self.terminal = terminal
        self.setLevel(logging.DEBUG)

    def emit(self, record):
        if not hasattr(self, 'terminal') or not self.terminal:
            return
            
        try:
            # Format the message with timestamp and level
            msg = self.format(record)
            if not msg.endswith("\n"):
                msg += "\n"
            
            # Determine the tag based on log level
            tag = "debug"
            if record.levelno >= logging.ERROR:
                tag = "error"
            elif record.levelno >= logging.WARNING:
                tag = "warning"
            elif record.levelno >= logging.INFO:
                tag = "info"
            
            # Insert the message at the end of the terminal
            self.terminal._textbox.configure(state="normal")  # Enable editing
            self.terminal._textbox.insert("end", msg, tag)
            self.terminal._textbox.see("end")  # Scroll to the end
            self.terminal._textbox.configure(state="disabled")  # Disable editing
            
        except Exception as e:
            print(f"Error in terminal_handler: {str(e)}")

    def format(self, record):
        # Create a custom format for the log message
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"{timestamp} - {record.levelname} - {record.getMessage()}"

class MinuxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize database first
        init_database()
        
        # Create notification frame first
        self.notification_frame = ctk.CTkFrame(self, fg_color="#FF4444", height=30, corner_radius=0)
        self.notification_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.notification_frame.grid_remove()  # Hidden by default
        
        # Error icon
        self.error_icon_label = ctk.CTkLabel(
            self.notification_frame,
            text="⚠",
            text_color="white",
            font=ctk.CTkFont(size=16)
        )
        self.error_icon_label.pack(side="left", padx=10)
        
        # Notification message
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            text_color="white",
            font=ctk.CTkFont(size=12)
        )
        self.notification_label.pack(side="left", fill="x", expand=True)
        
        # Close button
        close_btn = ctk.CTkButton(
            self.notification_frame,
            text="×",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#FF6666",
            command=self.hide_notification,
            font=ctk.CTkFont(size=16)
        )
        close_btn.pack(side="right", padx=5)
        
        # Initialize db attribute
        self.db = None
        self.offline_mode = False
        
        # Try to initialize Firebase
        try:
            if not firebase_admin._apps:
                if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                    logger.warning("Service account key file not found. Running in offline mode.")
                    self.offline_mode = True
                else:
                    try:
                        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                        firebase_admin.initialize_app(cred)
                        self.db = firestore.client()
                        logger.info("Firebase initialized successfully")
                    except Exception as e:
                        logger.warning(f"Failed to initialize Firebase. Running in offline mode. Error: {str(e)}")
                        self.offline_mode = True
            else:
                self.db = firestore.client()
                logger.info("Using existing Firebase connection")
        except Exception as e:
            logger.warning(f"Firebase initialization skipped. Running in offline mode. Error: {str(e)}")
            self.offline_mode = True
            
        if self.offline_mode:
            self.show_error_notification("Running in offline mode. Some features may be limited.")
            
        # VSCode-like colors
        self.vscode_colors = {
            'activity_bar': '#333333',
            'sidebar': '#252526',
            'editor_bg': '#1e1e1e',
            'panel_bg': '#1e1e1e',
            'status_bar': '#007acc',
            'tab_active': '#1e1e1e',
            'tab_inactive': '#2d2d2d',
            'tab_hover': '#404040'
        }

        # Configure the main window
        self.title("Minux")
        self.geometry("1200x800")
        
        # Set window icon
        try:
            icon_path = os.path.join("media", "images", "logo.png")
            if os.path.exists(icon_path):
                # Load and convert image
                icon_image = Image.open(icon_path)
                # Convert to RGBA if not already
                if icon_image.mode != 'RGBA':
                    icon_image = icon_image.convert('RGBA')
                # Create PhotoImage for the icon
                icon_photo = ImageTk.PhotoImage(icon_image)
                # Set the window icon
                self.wm_iconphoto(True, icon_photo)
                # Keep a reference to prevent garbage collection
                self.icon_photo = icon_photo
                # For Windows/WSL compatibility
                if platform.system() == "Windows" or "microsoft" in platform.uname().release.lower():
                    # Create a temporary .ico file
                    ico_path = os.path.join("media", "images", "temp_icon.ico")
                    icon_image.save(ico_path, format='ICO', sizes=[(32, 32)])
                    self.iconbitmap(ico_path)
                    # Clean up temporary file
                    try:
                        os.remove(ico_path)
                    except:
                        pass
                # Keep a reference to prevent garbage collection
                self.icon_photo = icon_photo
                logger.info("Application icon set successfully")
            else:
                logger.warning("Icon file not found at: " + icon_path)
        except Exception as e:
            logger.error(f"Failed to set application icon: {str(e)}")
        
        # Configure grid weights
        self.grid_columnconfigure(2, weight=1)  # Make tab view expand
        self.grid_rowconfigure(0, weight=1)
        
        # Create activity bar
        self.activity_bar = ctk.CTkFrame(self, fg_color=self.vscode_colors['activity_bar'], width=48, corner_radius=0)
        self.activity_bar.grid(row=0, column=0, sticky="ns")
        self.activity_bar.grid_propagate(False)
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=self.vscode_colors['sidebar'], width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid_remove()  # Hidden by default
        
        # Create tab view
        self.tab_view = TabView(self)
        self.tab_view.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        
        # Show welcome screen
        self.show_welcome_screen()
        
        # Create terminal panel
        self.terminal_frame = ctk.CTkFrame(self, fg_color=self.vscode_colors['panel_bg'], height=200, corner_radius=0)
        self.terminal_frame.grid(row=1, column=0, columnspan=4, sticky="ew")
        self.terminal_frame.grid_remove()  # Hide terminal by default
        self.terminal_frame.grid_propagate(False)
        self.terminal_visible = False  # Initialize terminal visibility state
        
        # Create status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=4, column=0, columnspan=4, sticky="ew")
        
        # Initialize warning/error counts
        self.warning_count = 0
        self.error_count = 0
        
        # Setup UI components
        self.setup_activity_bar()
        self.setup_sidebar()
        self.setup_terminal()
        self.setup_status_bar()
        
        # Create the main menu
        self.create_menu()

    def setup_activity_bar(self):
        try:
            icons_path = "media/icons"
            # Default icons using Unicode symbols
            default_icons = {
                "Explorer": "📁",
                "Search": "🔍",
                "Source Control": "📝",
                "Run and Debug": "🐞",
                "TODO List": "✓",
                "Music Theory": "♪",
                "Extensions": "🧩"
            }
            
            buttons = []
            for name, symbol in default_icons.items():
                icon = None
                icon_file = None
                
                # Try to load the corresponding icon file
                if name == "Explorer":
                    icon_file = "files.png"
                elif name == "Search":
                    icon_file = "search.png"
                elif name == "Source Control":
                    icon_file = "git.png"
                elif name == "Run and Debug":
                    icon_file = "debug.png"
                elif name == "TODO List":
                    icon_file = "todo.png"
                elif name == "Music Theory":
                    icon_file = "music_note.png"
                elif name == "Extensions":
                    icon_file = "extensions.png"
                
                # Try to load the icon file if it exists
                if icon_file:
                    try:
                        icon_path = os.path.join(icons_path, icon_file)
                        if os.path.exists(icon_path):
                            # Load and convert image to RGBA if it's the TODO icon
                            img = Image.open(icon_path)
                            if name == "TODO List":
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                # Create a white version of the icon
                                data = img.getdata()
                                newData = []
                                for item in data:
                                    # Change all non-transparent pixels to white
                                    if item[3] > 0:  # If pixel is not transparent
                                        newData.append((255, 255, 255, item[3]))
                                    else:
                                        newData.append(item)
                                img.putdata(newData)
                            icon = ctk.CTkImage(img, size=(24, 24))
                    except Exception as e:
                        logger.debug(f"Could not load icon {icon_file}: {str(e)}")
                
                # Create button with either icon or Unicode symbol
                btn = ctk.CTkButton(
                    self.activity_bar,
                    text="" if icon else symbol,
                    image=icon,
                    width=48,
                    height=48,
                    fg_color="transparent",
                    hover_color="#505050",
                    command=lambda w=name: self.handle_activity_button(w),
                    corner_radius=0,
                    font=ctk.CTkFont(size=20) if not icon else None
                )
                buttons.append((btn, name))
            
            # Add buttons to the activity bar
            for i, (btn, _) in enumerate(buttons):
                btn.grid(row=i, column=0, pady=(5, 0))
                
        except Exception as e:
            logger.error(f"Error setting up activity bar: {str(e)}")
            # Create minimal activity bar with text buttons if icons fail
            for i, name in enumerate(["Explorer", "Search", "Source Control", "Run and Debug", 
                                    "TODO List", "Music Theory", "Extensions"]):
                btn = ctk.CTkButton(
                    self.activity_bar,
                    text=name[0],  # Just use first letter
                    width=48,
                    height=48,
                    fg_color="transparent",
                    hover_color="#505050",
                    command=lambda w=name: self.handle_activity_button(w),
                    corner_radius=0
                )
                btn.grid(row=i, column=0, pady=(5, 0))

    def handle_activity_button(self, button_name):
        """Handle clicks on activity bar buttons"""
        if button_name == "Explorer":
            self.toggle_explorer()
        elif button_name == "Search":
            self.toggle_search()
        elif button_name == "Source Control":
            self.toggle_source_control()
        elif button_name == "Run and Debug":
            self.toggle_debug()
        elif button_name == "Extensions":
            self.toggle_extensions()
        elif button_name == "Music Theory":
            self.toggle_music_theory()
        elif button_name == "TODO List":
            self.toggle_todo()

    def toggle_todo(self):
        """Toggle the TODO sidebar and content"""
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_todo_sidebar()
            self.show_todo_content()

    def setup_todo_sidebar(self):
        """Setup the TODO sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="TODO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Create a frame for the TODO categories
        categories_frame = ctk.CTkScrollableFrame(self.sidebar, corner_radius=0)
        categories_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Add TODO categories
        categories = ["All Tasks", "Today", "Upcoming", "Completed"]
        for category in categories:
            btn = ctk.CTkButton(
                categories_frame,
                text=category,
                fg_color="transparent",
                hover_color="#404040",
                anchor="w",
                command=lambda c=category: self.show_todo_category(c),
                corner_radius=0
            )
            btn.pack(fill="x", pady=2)

    def show_todo_content(self):
        """Show the main TODO content area"""
        # Create a frame for the TODO content
        todo_frame = ctk.CTkFrame(self.tab_view, fg_color="#1E1E1E", corner_radius=0)
        
        # Add TODO widget content
        self.setup_todo_widget(todo_frame)
        
        # Add the frame to a new tab
        self.tab_view.add_tab("TODO", todo_frame)

    def show_todo_category(self, category):
        """Show tasks for the selected category"""
        # This would be implemented to filter tasks based on the category
        pass

    def setup_sidebar(self):
        # This will be populated based on the active activity bar button
        pass

    def setup_terminal(self):
        """Create and setup the terminal panel"""
        self.terminal_frame = ctk.CTkFrame(self, height=150, fg_color="#1E1E1E", corner_radius=0)
        
        # Add terminal header with controls
        header_frame = ctk.CTkFrame(self.terminal_frame, fg_color="#2D2D2D", height=25, corner_radius=0)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        # Left side: Terminal icon and title
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent", corner_radius=0)
        left_header.pack(side="left", fill="x", expand=True)
        
        terminal_icon = "⚡"
        header_label = ctk.CTkLabel(
            left_header, 
            text=f"{terminal_icon} TERMINAL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#CCCCCC"
        )
        header_label.pack(side="left", padx=10)
        
        # Right side: Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent", corner_radius=0)
        controls_frame.pack(side="right", fill="x")
        
        # Clear button
        clear_button = ctk.CTkButton(
            controls_frame,
            text="Clear",
            width=50,
            height=20,
            fg_color="transparent",
            hover_color="#4A4A4A",
            command=self.clear_terminal,
            font=ctk.CTkFont(size=11),
            corner_radius=0
        )
        clear_button.pack(side="left", padx=5)
        
        # Close button
        close_button = ctk.CTkButton(
            controls_frame,
            text="×",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#E81123",
            command=self.toggle_terminal,
            font=ctk.CTkFont(size=16),
            corner_radius=0
        )
        close_button.pack(side="left", padx=5)

        # Create a frame for the terminal with scrollbar
        terminal_container = ctk.CTkFrame(self.terminal_frame, fg_color="transparent", corner_radius=0)
        terminal_container.pack(fill="both", expand=True)

        # Terminal output area with scrolling
        self.terminal = ctk.CTkTextbox(
            terminal_container, 
            fg_color="#1E1E1E", 
            text_color="#FFFFFF",
            height=150,
            font=("Consolas" if platform.system() == "Windows" else "Monaco", 12),
            wrap="word",
            corner_radius=0
        )
        self.terminal.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(terminal_container, command=self.terminal.yview, corner_radius=0)
        scrollbar.pack(side="right", fill="y")
        self.terminal.configure(yscrollcommand=scrollbar.set)
        
        # Configure tags for different log levels
        self.terminal._textbox.tag_configure("error", foreground="#FF6B68")
        self.terminal._textbox.tag_configure("warning", foreground="#FFD700")
        self.terminal._textbox.tag_configure("info", foreground="#6A9955")
        self.terminal._textbox.tag_configure("debug", foreground="#FFFFFF")
        
        # Welcome message
        welcome_msg = "Welcome to Minux Terminal\n"
        welcome_msg += "=" * 50 + "\n"
        self.terminal._textbox.insert("end", welcome_msg)
        self.terminal._textbox.see("end")
        
        # Create and start the queue listener with the proper handler
        terminal_handler = TerminalHandler(self.terminal)
        self.log_listener = logging.handlers.QueueListener(
            log_queue,
            terminal_handler,
            respect_handler_level=True
        )
        self.log_listener.start()

    def setup_todo_widget(self, parent_frame):
        """Setup the TODO widget content"""
        # Add a title and instructions
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=0)
        header_frame.pack(pady=(10,0), padx=10, fill="x")
        
        title = ctk.CTkLabel(
            header_frame, 
            text="TODO List", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(side="left")
        
        help_text = ctk.CTkLabel(
            header_frame,
            text="✓ Click 'Done' column to mark complete\n✓ Right-click for more options",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        help_text.pack(side="right")
        
        # Entry frame for adding tasks
        entry_frame = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=0)
        entry_frame.pack(pady=10, padx=10, fill="x")
        
        task_var = ctk.StringVar()
        task_entry = ctk.CTkEntry(
            entry_frame, 
            textvariable=task_var,
            placeholder_text="Enter a new task...",
            height=35,
            corner_radius=0
        )
        task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Create tree frame
        tree_frame = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=0)
        tree_frame.pack(expand=True, fill="both", pady=10, padx=10)

        # Configure style for the treeview
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            borderwidth=0,
            rowheight=30
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1E1E1E",
            foreground="white",
            borderwidth=1
        )
        style.map("Custom.Treeview",
            background=[('selected', '#3B3B3B')],
            foreground=[('selected', 'white')]
        )

        # Create Treeview
        columns = ("task", "done", "completed_date")
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )
        
        # Configure columns
        tree.heading("task", text="Task", command=lambda: sort_tasks("task"))
        tree.heading("done", text="Done", command=lambda: sort_tasks("done"))
        tree.heading("completed_date", text="Completed Date", command=lambda: sort_tasks("completed_date"))
        tree.column("task", width=300)
        tree.column("done", width=70, anchor="center")
        tree.column("completed_date", width=150, anchor="center")

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(tree_frame, command=tree.yview, corner_radius=0)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(expand=True, fill="both")

        def add_task(event=None):
            task = task_var.get().strip()
            if not task:
                self.show_error_notification("Cannot add empty task")
                logger.warning("Cannot add empty task")
                return
                
            try:
                # Add to SQLite
                logger.info(f"Attempting to add task to SQLite: {task}")
                logger.debug(f"Database path: {DB_PATH}")
                
                if not os.path.exists(DB_PATH):
                    logger.error(f"Database file does not exist at {DB_PATH}")
                    self.show_error_notification("Database file not found")
                    return
                    
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verify table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
                if not cursor.fetchone():
                    logger.error("todos table does not exist in database")
                    self.show_error_notification("Database table not found")
                    conn.close()
                    return
                
                cursor.execute('''
                    INSERT INTO todos (task, done, created_date)
                    VALUES (?, 0, CURRENT_TIMESTAMP)
                ''', (task,))
                task_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                logger.info(f"Task added successfully to local database: {task} (ID: {task_id})")
                
                # If Firebase is available, sync to cloud
                if self.db is not None:
                    try:
                        doc_ref = self.db.collection('todos').document()
                        doc_ref.set({
                            'task': task,
                            'done': False,
                            'completed_date': '',
                            'created_date': firestore.SERVER_TIMESTAMP,
                            'local_id': task_id
                        })
                        logger.info(f"Task synced to Firebase: {task}")
                    except Exception as e:
                        logger.warning(f"Failed to sync task to Firebase: {str(e)}")
                
                load_tasks()
                task_entry.delete(0, "end")
            except Exception as e:
                error_msg = f"Failed to add task: {str(e)}"
                self.show_error_notification(error_msg)
                logger.error(error_msg)

        task_entry.bind('<Return>', add_task)

        add_task_btn = ctk.CTkButton(
            entry_frame,
            text="Add Task",
            command=add_task,
            height=35,
            corner_radius=0,
            fg_color="#4a7dfc",
            hover_color="#5a8ffc"
        )
        add_task_btn.pack(side="right")

        def toggle_done_status(item_id):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Get current status
                cursor.execute('SELECT done FROM todos WHERE id = ?', (item_id,))
                current_status = cursor.fetchone()[0]
                
                # Toggle status
                new_status = not bool(current_status)
                completed_date = 'CURRENT_TIMESTAMP' if new_status else 'NULL'
                
                cursor.execute(f'''
                    UPDATE todos 
                    SET done = ?, completed_date = {completed_date}
                    WHERE id = ?
                ''', (new_status, item_id))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Task status updated in local database: {item_id} -> {new_status}")
                
                # Sync with Firebase if available
                if self.db is not None:
                    try:
                        # Find Firebase document with matching local_id
                        docs = self.db.collection('todos').where('local_id', '==', item_id).limit(1).get()
                        for doc in docs:
                            doc.reference.update({
                                'done': new_status,
                                'completed_date': firestore.SERVER_TIMESTAMP if new_status else ''
                            })
                        logger.info(f"Task status synced to Firebase: {item_id}")
                    except Exception as e:
                        logger.warning(f"Failed to sync task status to Firebase: {str(e)}")
                
                load_tasks()
            except Exception as e:
                error_msg = f"Failed to update task status: {str(e)}"
                self.show_error_notification(error_msg)
                logger.error(error_msg)

        def edit_task():
            selected_item = tree.selection()
            if not selected_item:
                return
            
            item_id = selected_item[0]
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT task FROM todos WHERE id = ?', (item_id,))
                current_task = cursor.fetchone()[0]
                conn.close()
            except Exception as e:
                logger.error(f"Failed to fetch task for editing: {str(e)}")
                return

            edit_window = ctk.CTkToplevel(parent_frame)
            edit_window.title("Edit Task")
            edit_window.geometry("400x150")
            edit_window.transient(parent_frame)
            edit_window.grab_set()

            edit_var = ctk.StringVar(value=current_task)
            edit_entry = ctk.CTkEntry(
                edit_window,
                textvariable=edit_var,
                width=300,
                height=35,
                corner_radius=0
            )
            edit_entry.pack(pady=(20, 10), padx=20)

            def save_edit():
                new_task = edit_var.get().strip()
                if new_task:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute('UPDATE todos SET task = ? WHERE id = ?', (new_task, item_id))
                        conn.commit()
                        conn.close()
                        
                        logger.info(f"Task edited in local database: {current_task} -> {new_task}")
                        
                        # Sync with Firebase if available
                        if self.db is not None:
                            try:
                                docs = self.db.collection('todos').where('local_id', '==', item_id).limit(1).get()
                                for doc in docs:
                                    doc.reference.update({'task': new_task})
                                logger.info(f"Task edit synced to Firebase: {item_id}")
                            except Exception as e:
                                logger.warning(f"Failed to sync task edit to Firebase: {str(e)}")
                        
                        load_tasks()
                        edit_window.destroy()
                    except Exception as e:
                        error_msg = f"Failed to edit task: {str(e)}"
                        self.show_error_notification(error_msg)
                        logger.error(error_msg)

            save_btn = ctk.CTkButton(
                edit_window,
                text="Save",
                command=save_edit,
                width=100,
                corner_radius=0
            )
            save_btn.pack(pady=10)
            edit_entry.bind('<Return>', lambda e: save_edit())
            edit_entry.focus()

        def delete_task():
            selected_item = tree.selection()
            if not selected_item:
                return
                
            item_id = selected_item[0]
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT task FROM todos WHERE id = ?', (item_id,))
                task_name = cursor.fetchone()[0]
                conn.close()
                
                response = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
                if response:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM todos WHERE id = ?', (item_id,))
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"Task deleted from local database: {task_name}")
                    
                    # Sync with Firebase if available
                    if self.db is not None:
                        try:
                            docs = self.db.collection('todos').where('local_id', '==', item_id).limit(1).get()
                            for doc in docs:
                                doc.reference.delete()
                            logger.info(f"Task deletion synced to Firebase: {item_id}")
                        except Exception as e:
                            logger.warning(f"Failed to sync task deletion to Firebase: {str(e)}")
                    
                    load_tasks()
            except Exception as e:
                error_msg = f"Failed to delete task: {str(e)}"
                self.show_error_notification(error_msg)
                logger.error(error_msg)

        def toggle_done(event):
            column = tree.identify_column(event.x)
            item_id = tree.identify_row(event.y)
            if column == "#2" and item_id:  # Done column
                toggle_done_status(int(item_id))

        tree.bind("<Button-1>", toggle_done)

        # Context menu
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="✓ Mark as Done", command=lambda: toggle_done_status(int(tree.selection()[0])) if tree.selection() else None)
        context_menu.add_command(label="✎ Edit Task", command=edit_task)
        context_menu.add_separator()
        context_menu.add_command(label="🗑 Delete Task", command=delete_task)

        def popup(event):
            try:
                item = tree.identify_row(event.y)
                if item:
                    tree.selection_set(item)
                    context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        tree.bind("<Button-3>", popup)

        sort_order = {"task": True, "done": True, "completed_date": True}  # True for ascending

        def sort_tasks(column):
            sort_order[column] = not sort_order[column]  # Toggle sort order
            
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                order = "ASC" if sort_order[column] else "DESC"
                if column == "task":
                    cursor.execute(f'SELECT * FROM todos ORDER BY task {order}')
                elif column == "done":
                    cursor.execute(f'SELECT * FROM todos ORDER BY done {order}')
                elif column == "completed_date":
                    cursor.execute(f'SELECT * FROM todos ORDER BY completed_date {order} NULLS LAST')
                
                tasks = cursor.fetchall()
                conn.close()
                
                for item in tree.get_children():
                    tree.delete(item)
                
                for task in tasks:
                    done = 'Yes' if task[2] else 'No'
                    completed_date = task[4] if task[4] else ''
                    tree.insert("", tk.END, values=(task[1], done, completed_date), iid=str(task[0]))
                
            except Exception as e:
                error_msg = f"Failed to sort tasks: {str(e)}"
                self.show_error_notification(error_msg)
                logger.error(error_msg)

        def load_tasks():
            try:
                for item in tree.get_children():
                    tree.delete(item)
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM todos ORDER BY created_date DESC')
                tasks = cursor.fetchall()
                conn.close()
                
                for task in tasks:
                    done = 'Yes' if task[2] else 'No'
                    completed_date = task[4] if task[4] else ''
                    tree.insert("", tk.END, values=(task[1], done, completed_date), iid=str(task[0]))
                
                logger.info(f"Tasks loaded successfully from local database. Total tasks: {len(tasks)}")
            except Exception as e:
                error_msg = f"Failed to load tasks: {str(e)}"
                self.show_error_notification(error_msg)
                logger.error(error_msg)

        # Initial load of tasks
        load_tasks()

    def clear_terminal(self):
        """Clear the terminal content"""
        self.terminal.configure(state="normal")  # Enable editing
        self.terminal.delete("0.0", "end")  # Clear all content
        
        # Add welcome message
        welcome_msg = "Welcome to Minux Terminal\n"
        welcome_msg += "=" * 50 + "\n"
        self.terminal.insert("0.0", welcome_msg)
        
        self.terminal.see("end")  # Scroll to the end
        self.terminal.configure(state="disabled")  # Disable editing again

    def toggle_terminal(self):
        """Toggle the terminal panel visibility"""
        if self.terminal_visible:
            self.terminal_frame.grid_remove()
            self.terminal_visible = False
        else:
            self.terminal_frame.grid(row=1, column=0, columnspan=4, sticky="ew")
            self.terminal_visible = True

    def setup_status_bar(self):
        """Setup the status bar"""
        # Add status information
        status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            text_color="white",
            font=("Segoe UI", 10)
        )
        status_label.pack(side="left", padx=5)
        
        # Add time display
        self.status_bar_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            text_color="white",
            font=("Segoe UI", 10)
        )
        self.status_bar_label.pack(side="right", padx=5)

    def add_widget_to_tab(self, tab, widget_type):
        """Add a widget to a specific tab"""
        if widget_type == "TODO":
            # Create TODO widget frame
            todo_frame = ctk.CTkFrame(tab, fg_color="#1E1E1E", corner_radius=0)
            todo_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Add TODO widget content (reusing existing TODO implementation)
            self.setup_todo_widget(todo_frame)

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
                    
                    
    def save_transparency(self, transparency):
        with open('settings.txt', 'w') as file:
            file.write(str(transparency))
        
    def load_transparency(self):
        try:
            with open('settings.txt', 'r') as file:
                return float(file.read())
        except (FileNotFoundError, ValueError):
            return 1.0  # Default transparency

    def update_transparency(self, value):
        transparency = float(value)
        self.attributes('-alpha', transparency)
        self.save_transparency(transparency)
        
    def quit_app(self):
        self.log_listener.stop()  # Stop the queue listener before quitting
        self.quit()

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
        button_frame = ctk.CTkFrame(confirmation_dialog, corner_radius=0)
        button_frame.pack(fill='x', expand=True, pady=10)

        # Stylish buttons with custom colors and padding
        yes_button = ctk.CTkButton(button_frame, text="Yes", command=self.quit,
                                    fg_color="green", hover_color="light green", corner_radius=0)
        no_button = ctk.CTkButton(button_frame, text="No", command=confirmation_dialog.destroy,
                                fg_color="red", hover_color="light coral", corner_radius=0)
        
        yes_button.pack(side='left', fill='x', expand=True, padx=10)
        no_button.pack(side='right', fill='x', expand=True, padx=10)

        
    def show_settings(self):
        if not hasattr(self, 'settings_frame'):
            self.settings_frame = ctk.CTkFrame(self, width=400, height=300, corner_radius=0)
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
        self.chat_history = ctk.CTkTextbox(self.panel1, height=15, corner_radius=0, fg_color="#2e2e2e", text_color="white")
        self.chat_history.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Frame for the user input and send button
        input_frame = ctk.CTkFrame(self.panel1, corner_radius=0)
        input_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        # User input entry
        self.user_input = ctk.CTkEntry(input_frame, placeholder_text="Ask me anything...", corner_radius=0)
        self.user_input.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")

        # Send button with a modern look
        send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message, corner_radius=0, fg_color="#4a7dfc", hover_color="#5a8ffc")
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

        # Create a main frame to hold both the file list and details panel
        main_frame = ctk.CTkFrame(self.panel2, corner_radius=0)
        main_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        
        # Create a scrollable frame for the file list
        file_list_frame = ctk.CTkFrame(main_frame, corner_radius=0)
        file_list_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
        
        # Details Panel
        self.details_panel = ctk.CTkFrame(main_frame, width=300, corner_radius=0)
        self.details_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        scores_path = 'media/scores'
        if os.path.exists(scores_path):
            row = 0
            for file_name in os.listdir(scores_path):
                file_path = os.path.join(scores_path, file_name)
                if os.path.isfile(file_path):
                    file_button = ctk.CTkButton(file_list_frame, text=file_name, anchor="w", font=ctk.CTkFont(size=14), command=lambda f=file_path: self.show_file_details(f))
                    file_button.grid(row=row, column=0, pady=(5, 5), padx=(5, 5), sticky="ew")
                    row += 1
        
        # Display the panel after setting it up
        self.panel2.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def show_file_details(self, file_path):
        # Clear previous details
        for widget in self.details_panel.winfo_children():
            widget.destroy()

        file_name = os.path.basename(file_path)
        file_label = ctk.CTkLabel(self.details_panel, text=file_name, anchor="w", padx=20, font=ctk.CTkFont(size=16, weight="bold"))
        file_label.grid(row=0, column=0, pady=(10, 10), sticky="w")

        if file_path.endswith('.pdf'):
            pdf_info = self.get_pdf_info(file_path)
            info_label = ctk.CTkLabel(self.details_panel, text=pdf_info, anchor="w", padx=20, font=ctk.CTkFont(size=12))
            info_label.grid(row=1, column=0, pady=(5, 0), sticky="w")
        elif file_path.endswith('.mscz'):
            mscz_info = "MuseScore file"
            info_label = ctk.CTkLabel(self.details_panel, text=mscz_info, anchor="w", padx=20, font=ctk.CTkFont(size=12))
            info_label.grid(row=1, column=0, pady=(5, 0), sticky="w")

    def get_pdf_info(self, file_path):
        try:
            doc = fitz.open(file_path)
            info = doc.metadata
            pdf_info = f"Title: {info['title']}\nAuthor: {info['author']}\nPages: {doc.page_count}"
            return pdf_info
        except Exception as e:
            return f"Error reading PDF: {e}"
        
    

        

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

        # Remove panels but keep status bar visible
        self.panel1.grid_remove()
        self.panel2.grid_remove()
        self.panel3.grid_remove()
        
        # Ensure status bar remains visible
        self.status_bar_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def some_function(self):
        print("Button clicked!")

    def show_error_notification(self, message):
        """Display error message in notification bar and prepare terminal"""
        # Log the error message
        logger.error(message)
        
        # Update notification message
        self.notification_label.configure(text=message)
        
        # Show notification frame if it's hidden
        if not self.notification_frame.winfo_viewable():
            self.notification_frame.grid()
        
        # Make notification frame clickable
        self.notification_frame.bind("<Button-1>", lambda e: self.show_error_in_terminal(message))
        self.error_icon_label.bind("<Button-1>", lambda e: self.show_error_in_terminal(message))
        self.notification_label.bind("<Button-1>", lambda e: self.show_error_in_terminal(message))

    def hide_notification(self):
        """Hide the notification bar"""
        self.notification_frame.grid_remove()

    def show_error_in_terminal(self, message):
        """Show the terminal and display the error message"""
        # Show terminal if it's hidden
        if not self.terminal_visible:
            self.toggle_terminal()
        
        # Ensure terminal is visible
        self.terminal_frame.grid(row=1, column=0, columnspan=4, sticky="ew")
        self.terminal_visible = True
        
        # Log the error message to ensure it appears in the terminal
        logger.error(message)
        
        # Hide notification
        self.hide_notification()

    def toggle_explorer(self):
        """Toggle the file explorer sidebar"""
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_explorer_sidebar()

    def setup_explorer_sidebar(self):
        """Setup the explorer sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="EXPLORER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Create file explorer in sidebar
        self.explorer = FileExplorer(self.sidebar, self.on_file_select)
        self.explorer.pack(fill="both", expand=True, padx=5, pady=5)

    def toggle_search(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_search_sidebar()

    def setup_search_sidebar(self):
        """Setup the search sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="SEARCH",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Add search entry
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search...",
            height=30,
            corner_radius=0
        )
        search_entry.pack(fill="x", padx=5)

    def toggle_source_control(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_source_control_sidebar()

    def setup_source_control_sidebar(self):
        """Setup the source control sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="SOURCE CONTROL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Add placeholder content
        content = ctk.CTkLabel(
            self.sidebar,
            text="Source control features\ncoming soon...",
            text_color="#888888"
        )
        content.pack(pady=20)

    def toggle_debug(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_debug_sidebar()

    def setup_debug_sidebar(self):
        """Setup the debug sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="RUN AND DEBUG",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Add debug controls
        controls_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        start_btn = ctk.CTkButton(
            controls_frame,
            text="Start Debugging",
            height=30,
            corner_radius=0,
            command=lambda: print("Start debugging")
        )
        start_btn.pack(fill="x", pady=2)
        
        run_btn = ctk.CTkButton(
            controls_frame,
            text="Run Without Debugging",
            height=30,
            corner_radius=0,
            command=lambda: print("Run without debugging")
        )
        run_btn.pack(fill="x", pady=2)

    def toggle_extensions(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_extensions_sidebar()

    def setup_extensions_sidebar(self):
        """Setup the extensions sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="EXTENSIONS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Add search entry
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search extensions...",
            height=30,
            corner_radius=0
        )
        search_entry.pack(fill="x", padx=5)

        # Add placeholder content
        content = ctk.CTkLabel(
            self.sidebar,
            text="No extensions installed",
            text_color="#888888"
        )
        content.pack(pady=20)

    def toggle_music_theory(self):
        """Toggle the music theory sidebar and content"""
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_music_theory_sidebar()
            self.show_music_theory_content()

    def setup_music_theory_sidebar(self):
        """Setup the music theory sidebar content"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        # Add sidebar header
        header = ctk.CTkLabel(
            self.sidebar,
            text="MUSIC THEORY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6F6F6F"
        )
        header.pack(pady=(10, 5), padx=10, anchor="w")

        # Create a frame for the scale list
        scales_frame = ctk.CTkScrollableFrame(self.sidebar, corner_radius=0)
        scales_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # List of common scales
        scales = [
            "C Major", "G Major", "D Major", "A Major", "E Major",
            "B Major", "F# Major", "C# Major",
            "F Major", "Bb Major", "Eb Major", "Ab Major",
            "Db Major", "Gb Major", "Cb Major",
            "A minor", "E minor", "B minor", "F# minor",
            "C# minor", "G# minor", "D# minor", "A# minor",
            "D minor", "G minor", "C minor", "F minor",
            "Bb minor", "Eb minor", "Ab minor"
        ]

        for scale in scales:
            btn = ctk.CTkButton(
                scales_frame,
                text=scale,
                fg_color="transparent",
                hover_color="#404040",
                anchor="w",
                command=lambda s=scale: self.show_scale_details(s),
                corner_radius=0
            )
            btn.pack(fill="x", pady=2)

    def show_music_theory_content(self):
        """Show the main music theory content area"""
        # Create a new tab for music theory if it doesn't exist
        self.music_theory_tab = ctk.CTkFrame(self.tab_view)
        self.tab_view.add_tab("Music Theory", self.music_theory_tab)
            
        # Add welcome content
        welcome_label = ctk.CTkLabel(
            self.music_theory_tab,
            text="Welcome to Music Theory\nSelect a scale from the sidebar to view details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFFFFF"
        )
        welcome_label.pack(pady=20)

    def show_scale_details(self, scale_name):
        """Show the details of the selected scale"""
        # Ensure the music theory tab exists
        if not hasattr(self, 'music_theory_tab') or not self.music_theory_tab.winfo_exists():
            self.show_music_theory_content()
        
        # Clear existing content in the music theory tab
        for widget in self.music_theory_tab.winfo_children():
            widget.destroy()

        # Add scale title
        title = ctk.CTkLabel(
            self.music_theory_tab,
            text=f"{scale_name} Scale",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(20, 10))

        # Add scale notes
        notes_frame = ctk.CTkFrame(self.music_theory_tab, fg_color="transparent")
        notes_frame.pack(pady=10)
        
        # Get notes for the scale
        notes = self.get_scale_notes(scale_name)
        notes_label = ctk.CTkLabel(
            notes_frame,
            text=" - ".join(notes),
            font=ctk.CTkFont(size=18),
            text_color="#FFFFFF"
        )
        notes_label.pack()

        # Add staff view
        staff_frame = ctk.CTkFrame(self.music_theory_tab, fg_color="#2D2D2D")
        staff_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Create canvas for drawing the staff
        canvas = tk.Canvas(
            staff_frame,
            bg="#2D2D2D",
            height=200,
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Draw the grand staff
        self.draw_grand_staff(canvas, notes, scale_name)

    def draw_grand_staff(self, canvas, notes, scale_name):
        """Draw the grand staff with the given notes"""
        # Staff dimensions and positioning
        staff_width = 600
        line_spacing = 10
        treble_start_y = 50
        bass_start_y = 150
        staff_left_margin = 80  # Increased margin for clefs
        
        # Draw treble staff lines
        for i in range(5):
            y = treble_start_y + i * line_spacing
            canvas.create_line(staff_left_margin, y, staff_width, y, fill="white")
            
        # Draw bass staff lines
        for i in range(5):
            y = bass_start_y + i * line_spacing
            canvas.create_line(staff_left_margin, y, staff_width, y, fill="white")
            
        # Draw treble clef
        treble_clef = "𝄞"
        canvas.create_text(
            staff_left_margin - 20,
            treble_start_y + 2*line_spacing,
            text=treble_clef,
            fill="white",
            font=("Times", 40),
            anchor="e"
        )
        
        # Draw bass clef
        bass_clef = "𝄢"
        canvas.create_text(
            staff_left_margin - 20,
            bass_start_y + 2*line_spacing,
            text=bass_clef,
            fill="white",
            font=("Times", 40),
            anchor="e"
        )

        # Note positions relative to the staff lines (0 = middle line)
        note_positions = {
            "C": 6,  # Two ledger lines below treble staff
            "D": 5,
            "E": 4,
            "F": 3,
            "G": 2,
            "A": 1,
            "B": 0,
        }

        # Draw notes
        x = staff_left_margin + 50  # Starting x position for notes
        x_spacing = 60  # Space between notes
        
        for note in notes:
            base_note = note[0]  # Get the base note letter
            
            # Get the position from our note_positions dictionary
            if base_note in note_positions:
                position = note_positions[base_note]
                y = treble_start_y + position * (line_spacing/2)
                
                # Draw the note head
                canvas.create_oval(x-6, y-4, x+6, y+4, fill="white", outline="white")
                
                # Draw ledger lines if needed
                if position >= 6:  # Notes below the staff
                    for ledger_y in range(5, position + 1, 2):
                        line_y = treble_start_y + ledger_y * (line_spacing/2)
                        canvas.create_line(x-10, line_y, x+10, line_y, fill="white")
                
                # Draw accidentals if present
                if len(note) > 1:
                    accidental = note[1:]
                    if accidental == "#":
                        canvas.create_text(x-15, y, text="♯", fill="white", font=("Times", 16))
                    elif accidental == "b":
                        canvas.create_text(x-15, y, text="♭", fill="white", font=("Times", 16))
            
            x += x_spacing

        # Draw bar line at the end
        canvas.create_line(staff_width - 10, treble_start_y, staff_width - 10, treble_start_y + 4*line_spacing, fill="white", width=2)
        canvas.create_line(staff_width - 10, bass_start_y, staff_width - 10, bass_start_y + 4*line_spacing, fill="white", width=2)

    def get_scale_notes(self, scale_name):
        """Calculate the notes for a given scale"""
        # This is a simplified version - you would need to implement proper scale calculations
        notes = {
            "C Major": ["C", "D", "E", "F", "G", "A", "B"],
            "G Major": ["G", "A", "B", "C", "D", "E", "F#"],
            "D Major": ["D", "E", "F#", "G", "A", "B", "C#"],
            "A Major": ["A", "B", "C#", "D", "E", "F#", "G#"],
            "E Major": ["E", "F#", "G#", "A", "B", "C#", "D#"],
            "B Major": ["B", "C#", "D#", "E", "F#", "G#", "A#"],
            "F# Major": ["F#", "G#", "A#", "B", "C#", "D#", "E#"],
            "C# Major": ["C#", "D#", "E#", "F#", "G#", "A#", "B#"],
            "F Major": ["F", "G", "A", "Bb", "C", "D", "E"],
            "Bb Major": ["Bb", "C", "D", "Eb", "F", "G", "A"],
            "Eb Major": ["Eb", "F", "G", "Ab", "Bb", "C", "D"],
            "Ab Major": ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],
            "Db Major": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"],
            "Gb Major": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],
            "Cb Major": ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],
            # Add minor scales here
        }
        return notes.get(scale_name, ["C", "D", "E", "F", "G", "A", "B"])  # Default to C major if scale not found

    def on_file_select(self, file_path):
        # Check if file is already open in a tab
        if file_path in self.tab_view.tabs:
            self.tab_view.select_tab(file_path)
            return
        
        # Create new file viewer
        viewer = FileViewer(self.tab_view)
        viewer.load_file(file_path)
        
        # Add new tab
        self.tab_view.add_tab(file_path, viewer)

    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=lambda: self.new_file())
        file_menu.add_command(label="New Window", command=lambda: self.new_window())
        file_menu.add_separator()
        file_menu.add_command(label="Open File...", command=lambda: self.open_file())
        file_menu.add_command(label="Open Folder...", command=lambda: self.open_folder())
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda: self.save_file())
        file_menu.add_command(label="Save As...", command=lambda: self.save_file_as())
        file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=lambda: self.show_preferences())
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.undo())
        edit_menu.add_command(label="Redo", command=lambda: self.redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.cut())
        edit_menu.add_command(label="Copy", command=lambda: self.copy())
        edit_menu.add_command(label="Paste", command=lambda: self.paste())
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=lambda: self.find())
        edit_menu.add_command(label="Replace", command=lambda: self.replace())

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Terminal", command=self.toggle_terminal)
        view_menu.add_checkbutton(label="Problems", command=lambda: self.toggle_problems())
        view_menu.add_checkbutton(label="Output", command=lambda: self.toggle_output())
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Explorer", command=self.toggle_explorer)
        view_menu.add_checkbutton(label="Search", command=self.toggle_search)
        view_menu.add_checkbutton(label="Source Control", command=self.toggle_source_control)
        view_menu.add_checkbutton(label="Run and Debug", command=self.toggle_debug)
        view_menu.add_checkbutton(label="Extensions", command=self.toggle_extensions)

        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Start Debugging", command=lambda: self.start_debugging())
        run_menu.add_command(label="Run Without Debugging", command=lambda: self.run_without_debugging())
        run_menu.add_separator()
        run_menu.add_command(label="Toggle Breakpoint", command=lambda: self.toggle_breakpoint())

        # Terminal menu
        terminal_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Terminal", menu=terminal_menu)
        terminal_menu.add_command(label="New Terminal", command=lambda: self.new_terminal())
        terminal_menu.add_command(label="Split Terminal", command=lambda: self.split_terminal())
        terminal_menu.add_separator()
        terminal_menu.add_command(label="Clear", command=self.clear_terminal)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Welcome", command=lambda: self.show_welcome())
        help_menu.add_command(label="Documentation", command=lambda: self.show_documentation())
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: self.show_about())

        # Add placeholder methods for new menu items
        self.new_file = lambda: print("New File")
        self.new_window = lambda: print("New Window")
        self.open_file = lambda: print("Open File")
        self.open_folder = lambda: print("Open Folder")
        self.save_file = lambda: print("Save File")
        self.save_file_as = lambda: print("Save As")
        self.undo = lambda: print("Undo")
        self.redo = lambda: print("Redo")
        self.cut = lambda: print("Cut")
        self.copy = lambda: print("Copy")
        self.paste = lambda: print("Paste")
        self.find = lambda: print("Find")
        self.replace = lambda: print("Replace")
        self.toggle_problems = lambda: print("Toggle Problems")
        self.toggle_output = lambda: print("Toggle Output")
        self.start_debugging = lambda: print("Start Debugging")
        self.run_without_debugging = lambda: print("Run Without Debugging")
        self.toggle_breakpoint = lambda: print("Toggle Breakpoint")
        self.new_terminal = lambda: print("New Terminal")
        self.split_terminal = lambda: print("Split Terminal")
        self.show_welcome = lambda: print("Show Welcome")
        self.show_documentation = lambda: print("Show Documentation")
        self.show_about = lambda: print("Show About")

    def show_welcome_screen(self):
        """Show the welcome screen in the main content area"""
        welcome = WelcomeScreen(self.tab_view, self.handle_welcome_action)
        self.tab_view.add_tab("Welcome", welcome)
    
    def handle_welcome_action(self, action):
        """Handle actions from the welcome screen"""
        if isinstance(action, tuple):
            action_type, path = action
            if action_type == "open":
                if os.path.isdir(path):
                    self.open_folder(path)
                else:
                    self.open_file(path)
            elif action_type == "open_todo":
                # Show the TODO list and highlight the selected task
                self.toggle_todo()
        else:
            if action == "New File":
                self.new_file()
            elif action == "Open Folder":
                self.open_folder()
            elif action == "Clone Git Repository":
                self.clone_repository()
            elif action == "Open Terminal":
                self.toggle_terminal()
            elif action == "Get Started":
                self.show_getting_started()
            elif action == "Documentation":
                self.show_documentation()
            elif action == "Tips and Tricks":
                self.show_tips()
    
    def show_getting_started(self):
        """Show getting started guide"""
        # TODO: Implement getting started guide
        pass
    
    def show_tips(self):
        """Show tips and tricks"""
        # TODO: Implement tips and tricks
        pass
    
    def clone_repository(self):
        """Show dialog to clone a git repository"""
        # TODO: Implement repository cloning
        pass

    def show_preferences(self):
        """Show the settings/preferences tab"""
        # Create settings frame if it doesn't exist
        settings_frame = ctk.CTkFrame(self.tab_view, fg_color="#1e1e1e")
        
        # Create two-column layout
        left_column = ctk.CTkFrame(settings_frame, fg_color="transparent")
        left_column.pack(side="left", fill="y", padx=(20, 10), pady=20)
        
        right_column = ctk.CTkScrollableFrame(settings_frame, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)
        
        # Add search bar at the top
        search_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search settings",
            height=32,
            corner_radius=0
        )
        search_entry.pack(fill="x")
        
        # Add settings categories
        categories = [
            "Commonly Used",
            "Text Editor",
            "Workbench",
            "Window",
            "Features",
            "Application",
            "Security",
            "Extensions"
        ]
        
        for category in categories:
            btn = ctk.CTkButton(
                left_column,
                text=category,
                fg_color="transparent",
                hover_color="#2a2d2e",
                anchor="w",
                height=32,
                corner_radius=0,
                command=lambda c=category: self.show_settings_category(c, right_column)
            )
            btn.pack(fill="x", pady=1)
        
        # Show initial category (Commonly Used)
        self.show_settings_category("Commonly Used", right_column)
        
        # Add the settings to the tab view
        self.tab_view.add_tab("Settings", settings_frame)

    def show_settings_category(self, category, container):
        """Show settings for the selected category"""
        # Clear existing content
        for widget in container.winfo_children():
            widget.destroy()
            
        # Add category title
        title = ctk.CTkLabel(
            container,
            text=category,
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.pack(fill="x", pady=(0, 20))
        
        if category == "Commonly Used":
            # Files: Auto Save
            self.create_setting_group(container, "Files", [
                {
                    "title": "Auto Save",
                    "description": "Controls auto save of editors that have unsaved changes.",
                    "type": "dropdown",
                    "options": ["off", "afterDelay", "onFocusChange", "onWindowChange"],
                    "default": "off"
                }
            ])
            
            # Editor settings
            self.create_setting_group(container, "Editor", [
                {
                    "title": "Font Size",
                    "description": "Controls the font size in pixels.",
                    "type": "number",
                    "default": "14"
                },
                {
                    "title": "Font Family",
                    "description": "Controls the font family.",
                    "type": "text",
                    "default": "Consolas, 'Courier New', monospace"
                },
                {
                    "title": "Tab Size",
                    "description": "The number of spaces a tab is equal to.",
                    "type": "number",
                    "default": "4"
                },
                {
                    "title": "Render Whitespace",
                    "description": "Controls how the editor should render whitespace characters.",
                    "type": "dropdown",
                    "options": ["none", "boundary", "selection", "all"],
                    "default": "selection"
                }
            ])

    def create_setting_group(self, container, title, settings):
        """Create a group of related settings"""
        # Group title
        group_title = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#6F6F6F",
            anchor="w"
        )
        group_title.pack(fill="x", pady=(0, 10))
        
        # Settings
        for setting in settings:
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", pady=(0, 15))
            
            # Title and description
            title_label = ctk.CTkLabel(
                frame,
                text=setting["title"],
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            title_label.pack(fill="x")
            
            desc_label = ctk.CTkLabel(
                frame,
                text=setting["description"],
                font=ctk.CTkFont(size=11),
                text_color="#8B8B8B",
                anchor="w"
            )
            desc_label.pack(fill="x")
            
            # Input control based on type
            if setting["type"] == "dropdown":
                dropdown = ctk.CTkOptionMenu(
                    frame,
                    values=setting["options"],
                    height=32,
                    corner_radius=0
                )
                dropdown.set(setting["default"])
                dropdown.pack(fill="x", pady=(5, 0))
            elif setting["type"] == "number":
                entry = ctk.CTkEntry(
                    frame,
                    height=32,
                    corner_radius=0
                )
                entry.insert(0, setting["default"])
                entry.pack(fill="x", pady=(5, 0))
            elif setting["type"] == "text":
                entry = ctk.CTkEntry(
                    frame,
                    height=32,
                    corner_radius=0
                )
                entry.insert(0, setting["default"])
                entry.pack(fill="x", pady=(5, 0))

# Configure database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'minux.db')

def init_database():
    """Initialize SQLite database and create necessary tables"""
    try:
        logger.info(f"Initializing database at {DB_PATH}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create todos table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                done BOOLEAN DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP,
                synced BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Verify the database was created
        if os.path.exists(DB_PATH):
            logger.info(f"Database initialized successfully at {DB_PATH}")
            logger.info(f"Database file size: {os.path.getsize(DB_PATH)} bytes")
        else:
            logger.error(f"Database file was not created at {DB_PATH}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.error(f"Stack trace: ", exc_info=True)

# Initialize database
init_database()

if __name__ == "__main__":
    try:
        app = MinuxApp()
        app.mainloop()
    except Exception as e:
        print(f"An exception occurred: {e}")
