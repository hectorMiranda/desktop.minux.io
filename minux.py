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
        
        # Initialize db attribute
        self.db = None
        
        # Try to initialize Firebase
        try:
            if not firebase_admin._apps:
                if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                    logger.warning(f"Service account key file not found at: {SERVICE_ACCOUNT_KEY_PATH}")
                else:
                    try:
                        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                        firebase_admin.initialize_app(cred)
                        self.db = firestore.client()
                        logger.info("Firebase initialized successfully")
                    except Exception as e:
                        logger.warning(f"Failed to initialize Firebase: {str(e)}")
            else:
                self.db = firestore.client()
                logger.info("Using existing Firebase connection")
        except Exception as e:
            logger.warning(f"Firebase initialization skipped: {str(e)}")
            
        # Create notification frame
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
        
        # Create terminal panel
        self.terminal_frame = ctk.CTkFrame(self, fg_color=self.vscode_colors['panel_bg'], height=200, corner_radius=0)
        self.terminal_frame.grid(row=1, column=0, columnspan=4, sticky="ew")
        self.terminal_frame.grid_remove()  # Hide terminal by default
        self.terminal_frame.grid_propagate(False)
        self.terminal_visible = False  # Initialize terminal visibility state
        
        # Create status bar
        self.status_bar = ctk.CTkFrame(self, fg_color=self.vscode_colors['status_bar'], height=25, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.status_bar.grid_propagate(False)
        
        # Setup UI components
        self.setup_activity_bar()
        self.setup_sidebar()
        self.setup_terminal()
        self.setup_status_bar()
        
        # Create the main menu
        self.create_menu()

    def setup_activity_bar(self):
        try:
            # Load icons
            explorer_icon = ctk.CTkImage(Image.open("media/icons/files.png"), size=(24, 24))
            search_icon = ctk.CTkImage(Image.open("media/icons/search.png"), size=(24, 24))
            git_icon = ctk.CTkImage(Image.open("media/icons/git.png"), size=(24, 24))
            debug_icon = ctk.CTkImage(Image.open("media/icons/debug.png"), size=(24, 24))
            extensions_icon = ctk.CTkImage(Image.open("media/icons/extensions.png"), size=(24, 24))
            
            # Create buttons
            buttons = [
                ("Explorer", explorer_icon),
                ("Search", search_icon),
                ("Source Control", git_icon),
                ("Debug", debug_icon),
                ("Extensions", extensions_icon)
            ]
            
            for i, (name, icon) in enumerate(buttons):
                btn = ctk.CTkButton(
                    self.activity_bar,
                    text="",
                    image=icon,
                    width=48,
                    height=48,
                    fg_color="transparent",
                    hover_color="#505050",
                    command=lambda w=name: self.toggle_explorer(),
                    corner_radius=0
                )
                btn.grid(row=i, column=0, pady=(5, 0))
                
        except Exception as e:
            print(f"Error loading activity bar icons: {e}")

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
                
            if self.db is None:
                self.show_error_notification("Database connection is not available. Tasks will not be saved.")
                logger.warning("Database connection is not available. Tasks will not be saved.")
                # Add task to local storage or display only
                tree.insert("", tk.END, values=(task, "No", ""), iid=str(len(tree.get_children())))
                task_entry.delete(0, "end")
                return
                
            try:
                doc_ref = self.db.collection('todos').document()
                doc_ref.set({
                    'task': task,
                    'done': False,
                    'completed_date': '',
                    'created_date': firestore.SERVER_TIMESTAMP
                })
                logger.info(f"Task added successfully: {task}")
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
                if self.db is None:
                    # Handle local-only mode
                    item_values = tree.item(item_id)['values']
                    new_status = "Yes" if item_values[1] == "No" else "No"
                    completed_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') if new_status == "Yes" else ""
                    tree.item(item_id, values=(item_values[0], new_status, completed_date))
                    logger.info(f"Task status updated (local): {item_values[0]} -> {new_status}")
                    return
                    
                task_info = self.db.collection('todos').document(item_id).get().to_dict()
                if task_info:
                    new_status = not task_info.get('done', False)
                    update_data = {'done': new_status}
                    if new_status:
                        update_data['completed_date'] = firestore.SERVER_TIMESTAMP
                    else:
                        update_data['completed_date'] = ''
                    self.db.collection('todos').document(item_id).update(update_data)
                    logging.info(f"Task status updated: {task_info.get('task', 'Unknown task')} -> {'Done' if new_status else 'Not Done'}")
                    load_tasks()
            except Exception as e:
                logging.error(f"Failed to update task status: {str(e)}")

        def edit_task():
            selected_item = tree.selection()
            if not selected_item:
                return
            
            item_id = selected_item[0]
            
            if self.db is None:
                # Handle local-only mode
                item_values = tree.item(item_id)['values']
                current_task = item_values[0]
            else:
                task_info = self.db.collection('todos').document(item_id).get().to_dict()
                if not task_info:
                    return
                current_task = task_info['task']

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
                    if self.db is None:
                        # Handle local-only mode
                        item_values = tree.item(item_id)['values']
                        tree.item(item_id, values=(new_task, item_values[1], item_values[2]))
                        logger.info(f"Task edited (local): {current_task} -> {new_task}")
                    else:
                        self.db.collection('todos').document(item_id).update({
                            'task': new_task
                        })
                        load_tasks()
                    edit_window.destroy()

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
            if selected_item:
                try:
                    item_id = selected_item[0]
                    
                    if self.db is None:
                        # Handle local-only mode
                        item_values = tree.item(item_id)['values']
                        task_name = item_values[0]
                    else:
                        task_info = self.db.collection('todos').document(item_id).get().to_dict()
                        task_name = task_info.get('task', 'Unknown task') if task_info else 'Unknown task'
                    
                    response = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
                    if response:
                        if self.db is None:
                            # Handle local-only mode
                            tree.delete(item_id)
                            logger.info(f"Task deleted (local): {task_name}")
                        else:
                            self.db.collection('todos').document(item_id).delete()
                            logger.info(f"Task deleted: {task_name}")
                            load_tasks()
                except Exception as e:
                    logging.error(f"Failed to delete task: {str(e)}")

        def toggle_done(event):
            column = tree.identify_column(event.x)
            item_id = tree.identify_row(event.y)
            if column == "#2" and item_id:  # Done column
                toggle_done_status(item_id)

        tree.bind("<Button-1>", toggle_done)

        # Context menu
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="✓ Mark as Done", command=lambda: toggle_done_status(tree.selection()[0]) if tree.selection() else None)
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
            
            if self.db is None:
                # Handle local-only mode
                tasks = []
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    tasks.append({
                        'id': item,
                        'task': values[0],
                        'done': values[1] == "Yes",
                        'completed_date': values[2]
                    })
            else:
                docs = self.db.collection('todos').stream()
                tasks = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    tasks.append(data)
            
            reverse = not sort_order[column]
            if column == "task":
                tasks.sort(key=lambda x: x['task'].lower(), reverse=reverse)
            elif column == "done":
                tasks.sort(key=lambda x: x.get('done', False), reverse=reverse)
            elif column == "completed_date":
                tasks.sort(key=lambda x: x.get('completed_date', ''), reverse=reverse)
            
            for item in tree.get_children():
                tree.delete(item)
            
            for task in tasks:
                done = 'Yes' if task.get('done') else 'No'
                completed_date = task.get('completed_date', '')
                if completed_date and isinstance(completed_date, datetime.datetime):
                    completed_date = completed_date.strftime('%Y-%m-%d %H:%M')
                tree.insert("", tk.END, values=(task['task'], done, completed_date), iid=task['id'])

        def load_tasks():
            if self.db is None:
                # In local-only mode, we don't need to reload tasks as they're already in the tree
                logger.info("Skipping task reload in local-only mode")
                return
                
            try:
                for item in tree.get_children():
                    tree.delete(item)
                    
                docs = self.db.collection('todos').stream()
                tasks = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    tasks.append(data)
                
                # Sort by created date by default
                tasks.sort(key=lambda x: x.get('created_date', datetime.datetime.min), reverse=True)
                
                for task in tasks:
                    done = 'Yes' if task.get('done') else 'No'
                    completed_date = task.get('completed_date', '')
                    if completed_date and isinstance(completed_date, datetime.datetime):
                        completed_date = completed_date.strftime('%Y-%m-%d %H:%M')
                    tree.insert("", tk.END, values=(task['task'], done, completed_date), iid=task['id'])
                
                logger.info(f"Tasks loaded successfully. Total tasks: {len(tasks)}")
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

    def setup_activity_bar(self):
        """Setup the VSCode-like activity bar with icons"""
        # Load and create activity bar buttons
        icon_size = (20, 20)
        button_configs = [
            ("files.png", "Explorer", self.toggle_explorer),
            ("search.png", "Search", self.toggle_search),
            ("git.png", "Source Control", self.toggle_source_control),
            ("debug.png", "Run and Debug", self.toggle_debug),
            ("extensions.png", "Extensions", self.toggle_extensions)
        ]
        
        for i, (icon_name, tooltip, command) in enumerate(button_configs):
            try:
                icon = ctk.CTkImage(
                    Image.open(f"./media/icons/{icon_name}").resize(icon_size),
                    size=icon_size
                )
                btn = ctk.CTkButton(
                    self.activity_bar,
                    image=icon,
                    text="",
                    width=48,
                    height=48,
                    fg_color="transparent",
                    hover_color="#404040",
                    command=command,
                    corner_radius=0
                )
                btn.grid(row=i, column=0, pady=(5, 0))
                
                # Create tooltip (you'll need to implement this)
                # self.create_tooltip(btn, tooltip)
                
            except Exception as e:
                logger.error(f"Failed to load icon {icon_name}: {str(e)}")

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

    def toggle_source_control(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_source_control_sidebar()

    def toggle_debug(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_debug_sidebar()

    def toggle_extensions(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
            self.setup_extensions_sidebar()

    def create_tab(self, title, content=None):
        """Create a new tab in the tab bar"""
        tab_frame = ctk.CTkFrame(
            self.tab_bar,
            fg_color=self.vscode_colors["tab_active"],
            height=35
        )
        tab_frame.pack(side="left", padx=1, fill="y")
        
        tab_label = ctk.CTkLabel(
            tab_frame,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color="#CCCCCC"
        )
        tab_label.pack(side="left", padx=10, pady=5)
        
        close_btn = ctk.CTkButton(
            tab_frame,
            text="×",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#404040",
            command=lambda: self.close_tab(tab_frame)
        )
        close_btn.pack(side="right", padx=5)
        
        return tab_frame

    def close_tab(self, tab_frame):
        """Close a tab"""
        tab_frame.destroy()

    def show_add_widget_dialog(self):
        """Show the dialog for adding new widgets"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Widget")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()

        # Create a title for the widget section
        title_label = ctk.CTkLabel(
            dialog,
            text="Available Widgets",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Create a scrollable frame for widgets
        scroll_frame = ctk.CTkScrollableFrame(dialog, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Widget categories
        categories = {
            "Productivity": [
                ("TODO List", "todo", "Manage your tasks and to-dos"),
                ("Notes", "notes", "Take and organize notes"),
                ("Calendar", "calendar", "View and manage your schedule")
            ],
            "Tools": [
                ("Clock", Clock, "Display current time"),
                ("Timer", Timer, "Set countdown timers"),
                ("StopWatch", StopWatch, "Track elapsed time"),
                ("Alarm", Alarm, "Set alarms")
            ],
            "Fun": [
                ("Doge", Doge, "A fun Doge widget")
            ]
        }

        for category, widgets in categories.items():
            # Category label
            category_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", corner_radius=0)
            category_frame.pack(fill="x", pady=(10, 5))
            
            category_label = ctk.CTkLabel(
                category_frame,
                text=category,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            category_label.pack(anchor="w")

            # Widget buttons
            for widget_name, widget_class, description in widgets:
                widget_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", corner_radius=0)
                widget_frame.pack(fill="x", pady=5)
                
                btn = ctk.CTkButton(
                    widget_frame,
                    text=widget_name,
                    command=lambda w=widget_class: self.add_widget_from_dialog(w, dialog),
                    width=150,
                    height=32,
                    corner_radius=0
                )
                btn.pack(side="left", padx=(20, 10))
                
                desc_label = ctk.CTkLabel(
                    widget_frame,
                    text=description,
                    font=ctk.CTkFont(size=12),
                    text_color="#888888"
                )
                desc_label.pack(side="left")

    def add_widget_from_dialog(self, widget_class, dialog):
        """Add a widget from the dialog and close it"""
        if isinstance(widget_class, str):
            self.add_widget(widget_class)
        else:
            self.add_widget_instance(widget_class)
        dialog.destroy()

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
        file_menu.add_command(label="New Widget", command=self.show_add_widget_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Terminal", command=self.toggle_terminal)
        view_menu.add_checkbutton(label="Sidebar", command=self.toggle_explorer)

        # TODO menu
        todo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="TODO", menu=todo_menu)
        todo_menu.add_command(label="See TODO List", command=self.show_todo_list)

        # Themes menu
        themes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Themes", menu=themes_menu)
        themes_menu.add_command(label="Blue (Default)", command=lambda: self.change_theme("blue"))
        themes_menu.add_command(label="Green", command=lambda: self.change_theme("green"))
        themes_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))
        themes_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        themes_menu.add_command(label="System", command=lambda: self.change_theme("system"))

    def show_todo_list(self):
        """Open the TODO widget in a new tab"""
        todo_widget = TodoWidget(self.tab_view)
        self.tab_view.add_tab("TODO", todo_widget)

    def change_theme(self, theme_name):
        """Change the application's color theme"""
        if theme_name == "blue":
            ctk.set_default_color_theme("blue")
        elif theme_name == "green":
            ctk.set_default_color_theme("green")
        elif theme_name == "dark":
            ctk.set_appearance_mode("Dark")
        elif theme_name == "light":
            ctk.set_appearance_mode("Light")
        elif theme_name == "system":
            ctk.set_appearance_mode("System")
        
        # Refresh the UI to apply the new theme
        self.update()

if __name__ == "__main__":
    try:
        app = MinuxApp()
        app.mainloop()
    except Exception as e:
        print(f"An exception occurred: {e}")
