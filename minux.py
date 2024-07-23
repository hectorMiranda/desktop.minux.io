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


ctk.set_appearance_mode("Light")  
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

# Initialize Firebase with proper error handling
try:
    if not firebase_admin._apps:
        if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
            logger.error(f"Service account key file not found at: {SERVICE_ACCOUNT_KEY_PATH}")
            db = None
        else:
            try:
                with open(SERVICE_ACCOUNT_KEY_PATH, 'r') as f:
                    json.load(f)  # Validate JSON format
                cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                logger.info("Firebase initialized successfully")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format in service account key file: {SERVICE_ACCOUNT_KEY_PATH}")
                db = None
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with error: {str(e)}")
                db = None
    else:
        db = firestore.client()
        logger.info("Using existing Firebase connection")
except Exception as e:
    logger.error(f"Unexpected error during Firebase initialization: {str(e)}")
    db = None

class App(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.title("Minux")
        self.geometry("1100x580")
        self.db = db  # Store the database connection
        if self.db is None:
            logger.error("Application started without database connection")

        # Create menu bar
        self.create_menu()

        # Configure main grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(3, weight=0)  # For terminal
        self.grid_rowconfigure(4, weight=0)  # For status bar
        self.grid_rowconfigure(5, weight=0)  # For notification bar

        # Create notification bar (hidden by default)
        self.notification_frame = ctk.CTkFrame(self, height=25, fg_color="#2D2D2D")
        self.notification_frame.grid(row=5, column=0, columnspan=4, sticky="nsew")
        self.notification_frame.grid_columnconfigure(1, weight=1)
        self.notification_frame.grid_propagate(False)
        
        # Error icon and message label
        self.error_icon_label = ctk.CTkLabel(
            self.notification_frame,
            text="⚠",  # Warning icon
            font=ctk.CTkFont(size=14),
            text_color="#FF6B68",
            width=25
        )
        self.error_icon_label.grid(row=0, column=0, padx=(5, 0))
        
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B68",
            anchor="w"
        )
        self.notification_label.grid(row=0, column=1, sticky="w", padx=5)
        
        # Close notification button
        self.close_notification_btn = ctk.CTkButton(
            self.notification_frame,
            text="×",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color="#E81123",
            command=self.hide_notification,
            font=ctk.CTkFont(size=14),
            corner_radius=0
        )
        self.close_notification_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Hide notification bar initially
        self.notification_frame.grid_remove()

        icon_size = (50, 50)
        logging.info(platform.system())
        
        if platform.system() == "Windows":
            self.state("zoomed")
        elif platform.system() == "Darwin": 
            #self.attributes("-fullscreen", True)
            print("Darwin")
        else:
            self.attributes('-zoomed', True)

        # Create and show terminal frame by default
        self.terminal_visible = False  # Changed to False to hide by default
        self.create_terminal()
        self.terminal_frame.grid(row=3, column=0, columnspan=4, sticky="nsew")
        self.terminal_frame.grid_remove()  # Hide terminal by default

        # Initialize other components
        self.config = configparser.ConfigParser()
        self.config.read('configs/minux.ini') 
        self.logo_path = self.config.get('images', 'logo')  
        logo_pil = Image.open(self.logo_path).resize((106, 95))         
        self.logo_image = ctk.CTkImage(dark_image=logo_pil, light_image=logo_pil, size=(106, 95))
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
        self.sidebar.add_button("Data Science", self.show_conversation)
        
        # Create status bar frame (always visible)
        self.status_bar_frame = ctk.CTkFrame(self, height=icon_size[0], fg_color="gray", corner_radius=0)
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.status_bar_frame.grid_columnconfigure(1, weight=1)
        self.status_bar_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Configure status bar elements
        self.power_button = ctk.CTkButton(self.status_bar_frame, image=self.power_image, command=self.quit_app, width=icon_size[0], height=icon_size[1], fg_color="gray", text="", hover_color="red", corner_radius=0)
        self.power_button.grid(row=0, column=0, padx=1, pady=1)
        
        self.status_button_2 = ctk.CTkButton(self.status_bar_frame, text="Conversation", command=self.show_conversation, height=icon_size[1], corner_radius=0, hover_color="black")
        self.status_button_2.grid(row=0, column=1, padx=3, sticky="w")
        
        self.settings_button = ctk.CTkButton(self.status_bar_frame, text="", image=self.settings_image, command=self.show_settings, fg_color="gray", hover_color="orange", corner_radius=0, width=100)
        self.settings_button.grid(row=0, column=2, padx=1, sticky="w")
        
        self.status_bar_label = ctk.CTkLabel(self.status_bar_frame, text="")
        self.status_bar_label.grid(row=0, column=3, padx=1, sticky="e")
        self.update_time()
        
        # Ensure status bar is always visible by configuring grid weights
        self.grid_rowconfigure(4, weight=0, minsize=icon_size[1])  # Fixed height for status bar
        
        # Sidebar buttons
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

        self.widgets = []

        self.show_dashboard()
        
    def create_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit_app)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Terminal", command=self.toggle_terminal)

    def create_terminal(self):
        self.terminal_frame = ctk.CTkFrame(self, height=150, fg_color="#1E1E1E")
        
        # Add terminal header with controls
        header_frame = ctk.CTkFrame(self.terminal_frame, fg_color="#2D2D2D", height=25)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        # Left side: Terminal icon and title
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
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
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
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
            corner_radius=3
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

        # Terminal output area with scrolling
        self.terminal = ctk.CTkTextbox(
            self.terminal_frame, 
            fg_color="#1E1E1E", 
            text_color="#FFFFFF",
            height=150,
            font=("Consolas" if platform.system() == "Windows" else "Monaco", 12)
        )
        self.terminal.pack(fill="both", expand=True)
        
        # Configure tags for different log levels using the underlying tkinter Text widget
        self.terminal._textbox.tag_configure("error", foreground="#FF6B68")
        self.terminal._textbox.tag_configure("warning", foreground="#FFD700")
        self.terminal._textbox.tag_configure("info", foreground="#6A9955")
        self.terminal._textbox.tag_configure("debug", foreground="#FFFFFF")
        
        # Welcome message
        welcome_msg = "Welcome to Minux Terminal\n"
        welcome_msg += "=" * 50 + "\n"
        self.terminal._textbox.insert("end", welcome_msg)
        
        # Create and start the queue listener
        self.log_listener = logging.handlers.QueueListener(
            log_queue,
            self.terminal_handler,
            respect_handler_level=True
        )
        self.log_listener.start()

    def clear_terminal(self):
        """Clear the terminal content"""
        # Clear all text
        self.terminal.delete("0.0", "end")
        
        # Insert welcome message
        welcome_msg = "Welcome to Minux Terminal\n"
        welcome_msg += "=" * 50 + "\n"
        self.terminal.insert("0.0", welcome_msg)
        
        # Force update
        self.terminal.update()
        self.terminal._textbox.see("end")

    def terminal_handler(self, record):
        """Handle log records and display them in the terminal"""
        if not hasattr(self, 'terminal'):
            return
            
        try:
            # Format the message with timestamp and level
            msg = f"{record.asctime} - {record.levelname} - {record.message}"
            
            # Add traceback information for errors
            if record.exc_info:
                import traceback
                msg += "\n" + "".join(traceback.format_exception(*record.exc_info))
            
            # Ensure message ends with newline
            if not msg.endswith("\n"):
                msg += "\n"
            
            # Determine the tag based on log level
            if record.levelno >= logging.ERROR:
                tag = "error"
            elif record.levelno >= logging.WARNING:
                tag = "warning"
            elif record.levelno >= logging.INFO:
                tag = "info"
            else:
                tag = "debug"
            
            # Insert the message with the appropriate tag using the underlying Text widget
            self.terminal._textbox.insert("end", msg, tag)
            
            # Scroll to the end
            self.terminal._textbox.see("end")
            
            # Force update the UI
            self.terminal._textbox.update()
            
        except Exception as e:
            print(f"Error in terminal_handler: {str(e)}")  # Fallback error handling

    def toggle_terminal(self):
        if self.terminal_visible:
            self.terminal_frame.grid_remove()
            self.terminal_visible = False
        else:
            self.terminal_frame.grid(row=3, column=0, columnspan=4, sticky="nsew")
            self.terminal_visible = True

    def show_add_widget_dialog(self):
        self.clear_panels()
        
        # Create a title for the media section
        title_label = ctk.CTkLabel(self.panel1, text="Media Dashboard", anchor="w", padx=20, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")

        # Create a toolbar frame for media options
        media_toolbar = ctk.CTkFrame(self.panel1)
        media_toolbar.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        media_toolbar.grid_columnconfigure((0, 1), weight=1)

        # Add media widget buttons with modern styling
        todo_button = ctk.CTkButton(
            media_toolbar, 
            text="TODO Widget",
            command=lambda: self.add_widget("TODO"),
            fg_color="#2B2B2B",
            hover_color="#3B3B3B",
            height=40,
            corner_radius=8
        )
        todo_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        voice_button = ctk.CTkButton(
            media_toolbar, 
            text="Voice Recorder",
            command=lambda: self.add_widget("Voice"),
            fg_color="#2B2B2B",
            hover_color="#3B3B3B",
            height=40,
            corner_radius=8
        )
        voice_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Add a content area for widgets
        self.widget_area = ctk.CTkFrame(self.panel1)
        self.widget_area.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.panel1.grid_rowconfigure(2, weight=1)

        # Display the panel
        self.panel1.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def add_widget(self, widget_type):
        if not hasattr(self, 'widget_area'):
            return

        if widget_type == "TODO":
            # Create a frame for the TODO widget
            todo_frame = ctk.CTkFrame(self.widget_area, fg_color="#1E1E1E", corner_radius=8)
            todo_frame.grid(row=len(self.widgets), column=0, pady=10, padx=20, sticky="nsew")
            self.widget_area.grid_columnconfigure(0, weight=1)
            
            # Add a title and instructions
            header_frame = ctk.CTkFrame(todo_frame, fg_color="transparent")
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
            entry_frame = ctk.CTkFrame(todo_frame, fg_color="transparent")
            entry_frame.pack(pady=10, padx=10, fill="x")
            
            task_var = ctk.StringVar()
            task_entry = ctk.CTkEntry(
                entry_frame, 
                textvariable=task_var,
                placeholder_text="Enter a new task...",
                height=35,
                corner_radius=8
            )
            task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            def add_task(event=None):  # Allow Enter key to add task
                task = task_var.get().strip()
                if not task:
                    self.show_error_notification("Cannot add empty task")
                    logger.warning("Cannot add empty task")
                    return
                    
                if self.db is None:
                    error_msg = "Database connection is not available"
                    self.show_error_notification(error_msg)
                    logger.error(f"Cannot add task: {error_msg}")
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

            task_entry.bind('<Return>', add_task)  # Bind Enter key to add_task

            add_task_btn = ctk.CTkButton(
                entry_frame,
                text="Add Task",
                command=add_task,
                height=35,
                corner_radius=8,
                fg_color="#4a7dfc",
                hover_color="#5a8ffc"
            )
            add_task_btn.pack(side="right")

            # Create tree frame
            tree_frame = ctk.CTkFrame(todo_frame, fg_color="transparent")
            tree_frame.pack(expand=True, fill="both", pady=10, padx=10)

            # Configure style for the treeview
            style = ttk.Style()
            style.configure(
                "Custom.Treeview",
                background="#2B2B2B",
                foreground="white",
                fieldbackground="#2B2B2B",
                borderwidth=0,
                rowheight=30  # Increase row height for better visibility
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

            # Create Treeview with custom style
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
            scrollbar = ctk.CTkScrollbar(tree_frame, command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(expand=True, fill="both")

            # Enhanced context menu
            context_menu = tk.Menu(tree, tearoff=0)
            context_menu.add_command(label="✓ Mark as Done", command=lambda: toggle_done_menu())
            context_menu.add_command(label="✎ Edit Task", command=lambda: edit_task())
            context_menu.add_separator()
            context_menu.add_command(label="🗑 Delete Task", command=lambda: delete_task())

            def popup(event):
                try:
                    item = tree.identify_row(event.y)
                    if item:
                        tree.selection_set(item)
                        context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    context_menu.grab_release()

            tree.bind("<Button-3>", popup)

            def toggle_done_menu():
                selected_item = tree.selection()
                if selected_item:
                    toggle_done_status(selected_item[0])

            def toggle_done_status(item_id):
                try:
                    if self.db is None:
                        logging.error("Cannot update task: Database connection is not available")
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

            def toggle_done(event):
                column = tree.identify_column(event.x)
                item_id = tree.identify_row(event.y)
                if column == "#2" and item_id:  # Done column
                    toggle_done_status(item_id)

            tree.bind("<Button-1>", toggle_done)

            def edit_task():
                selected_item = tree.selection()
                if not selected_item:
                    return
                
                item_id = selected_item[0]
                task_info = self.db.collection('todos').document(item_id).get().to_dict()
                if not task_info:
                    return

                edit_window = ctk.CTkToplevel(todo_frame)
                edit_window.title("Edit Task")
                edit_window.geometry("400x150")
                edit_window.transient(todo_frame)
                edit_window.grab_set()

                edit_var = ctk.StringVar(value=task_info['task'])
                edit_entry = ctk.CTkEntry(
                    edit_window,
                    textvariable=edit_var,
                    width=300,
                    height=35
                )
                edit_entry.pack(pady=(20, 10), padx=20)

                def save_edit():
                    new_task = edit_var.get().strip()
                    if new_task:
                        self.db.collection('todos').document(item_id).update({
                            'task': new_task
                        })
                        load_tasks()
                        edit_window.destroy()

                save_btn = ctk.CTkButton(
                    edit_window,
                    text="Save",
                    command=save_edit,
                    width=100
                )
                save_btn.pack(pady=10)
                edit_entry.bind('<Return>', lambda e: save_edit())
                edit_entry.focus()

            def delete_task():
                selected_item = tree.selection()
                if selected_item:
                    try:
                        item_id = selected_item[0]
                        task_info = self.db.collection('todos').document(item_id).get().to_dict()
                        task_name = task_info.get('task', 'Unknown task') if task_info else 'Unknown task'
                        
                        response = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
                        if response:
                            if self.db is None:
                                logging.error("Cannot delete task: Database connection is not available")
                                return
                                
                            self.db.collection('todos').document(item_id).delete()
                            logging.info(f"Task deleted: {task_name}")
                            tree.delete(item_id)
                            load_tasks()
                    except Exception as e:
                        logging.error(f"Failed to delete task: {str(e)}")

            sort_order = {"task": True, "done": True, "completed_date": True}  # True for ascending

            def sort_tasks(column):
                sort_order[column] = not sort_order[column]  # Toggle sort order
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
                    if completed_date:
                        if isinstance(completed_date, datetime.datetime):
                            completed_date = completed_date.strftime('%Y-%m-%d %H:%M')
                    tree.insert("", tk.END, values=(task['task'], done, completed_date), iid=task['id'])

            def load_tasks():
                if self.db is None:
                    error_msg = "Database connection is not available"
                    self.show_error_notification(error_msg)
                    logger.error(f"Cannot load tasks: {error_msg}")
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
            
            widget = todo_frame
            
        elif widget_type == "Voice":
            widget = ctk.CTkLabel(self.widget_area, text="Voice Recorder Widget", fg_color="#1E1E1E", corner_radius=8)
            widget.grid(row=len(self.widgets), column=0, pady=10, padx=20, sticky="ew")
        
        if widget:
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

        # Create a main frame to hold both the file list and details panel
        main_frame = ctk.CTkFrame(self.panel2)
        main_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)

        # Create a scrollable frame for the file list
        file_list_frame = ctk.CTkFrame(main_frame)
        file_list_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
        file_list_frame.grid_rowconfigure(0, weight=1)
        file_list_frame.grid_columnconfigure(0, weight=1)

        # Scrollable Canvas
        canvas = ctk.CTkCanvas(file_list_frame, bg="white")
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(file_list_frame, orientation="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        file_list_inner_frame = ctk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=file_list_inner_frame, anchor="nw")

        file_list_inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Details Panel
        self.details_panel = ctk.CTkFrame(main_frame, width=300)
        self.details_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.details_panel.grid_columnconfigure(0, weight=1)
        self.details_panel.grid_rowconfigure(0, weight=1)

        scores_path = 'media/scores'
        if os.path.exists(scores_path):
            row = 0
            for file_name in os.listdir(scores_path):
                file_path = os.path.join(scores_path, file_name)
                if os.path.isfile(file_path):
                    file_button = ctk.CTkButton(file_list_inner_frame, text=file_name, anchor="w", font=ctk.CTkFont(size=14), command=lambda f=file_path: self.show_file_details(f))
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
        self.status_bar_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")

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
        self.terminal_frame.grid(row=3, column=0, columnspan=4, sticky="nsew")
        self.terminal_visible = True
        
        # Log the error message to ensure it appears in the terminal
        logger.error(message)
        
        # Hide notification
        self.hide_notification()

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"An exception occurred: {e}")
