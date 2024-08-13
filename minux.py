import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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

# Configure logging first
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

# Set dark mode as default
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# Configure logging to write to a queue
log_queue = queue.Queue()
queue_handler = logging.handlers.QueueHandler(log_queue)
logger.addHandler(queue_handler)

os.environ["PYTHONWARNINGS"] = "ignore:ApplePersistenceIgnoreState"

# Log the Python path and current directory
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current directory: {os.getcwd()}")
logger.debug(f"Script directory: {current_dir}")

SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', 'service_account_key.json')

class TerminalHandler(logging.Handler):
    def __init__(self, terminal):
        super().__init__()
        self.terminal = terminal
        self.setLevel(logging.DEBUG)
        
        # Configure text tags for different log levels
        self.terminal._textbox.tag_configure("debug", foreground="#6D6D6D")  # Gray
        self.terminal._textbox.tag_configure("info", foreground="#CCCCCC")   # Light gray
        self.terminal._textbox.tag_configure("warning", foreground="#FFA500")  # Orange
        self.terminal._textbox.tag_configure("error", foreground="#FF6B68")    # Red
        self.terminal._textbox.tag_configure("critical", foreground="#FF0000", underline=1)  # Bold red
        self.terminal._textbox.tag_configure("timestamp", foreground="#4EC9B0")  # Teal
        self.terminal._textbox.tag_configure("level", foreground="#569CD6")     # Blue

    def emit(self, record):
        if not hasattr(self, 'terminal') or not self.terminal:
            return
            
        try:
            # Format the message components
            timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            level_name = record.levelname.ljust(8)  # Pad level name for alignment
            msg = record.getMessage()
            
            # Determine the tag based on log level
            level_tag = "debug"
            if record.levelno >= logging.CRITICAL:
                level_tag = "critical"
            elif record.levelno >= logging.ERROR:
                level_tag = "error"
            elif record.levelno >= logging.WARNING:
                level_tag = "warning"
            elif record.levelno >= logging.INFO:
                level_tag = "info"
            
            # Insert the message components with appropriate tags
            self.terminal._textbox.configure(state="normal")  # Enable editing
            
            # Insert timestamp
            self.terminal._textbox.insert("end", f"{timestamp} ", "timestamp")
            
            # Insert level
            self.terminal._textbox.insert("end", f"{level_name} ", "level")
            
            # Insert message with appropriate tag
            self.terminal._textbox.insert("end", f"{msg}\n", level_tag)
            
            self.terminal._textbox.see("end")  # Scroll to the end
            self.terminal._textbox.configure(state="disabled")  # Disable editing
            
        except Exception as e:
            print(f"Error in terminal_handler: {str(e)}")

    def format(self, record):
        # Create a custom format for the log message
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"{timestamp} - {record.levelname} - {record.getMessage()}"

class VSCodeTabview(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        # Remove the segmented button options from kwargs to prevent interference
        for key in ["segmented_button_fg_color", "segmented_button_selected_color", 
                   "segmented_button_unselected_color", "segmented_button_selected_hover_color",
                   "segmented_button_unselected_hover_color"]:
            kwargs.pop(key, None)
            
        kwargs["fg_color"] = "#252526"  # VSCode tab bar background
        super().__init__(master, **kwargs)
        
        # Initialize tab-related attributes
        self._tab_dict = {}
        self._close_buttons = {}
        
        # Create an initial empty tab to prevent None current_name
        initial_tab = self.add("initial")
        self._current_name = "initial"  # Set current name explicitly
        
        # Configure the tab view appearance
        self._configure_tab_view()
        
        # Remove the initial tab
        self.delete("initial")
        
        # Configure grid weights for expansion
        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(0, weight=1)
        
        # Make the tab view expand to fill available space
        self.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        
    def _configure_tab_view(self):
        """Configure the tab view appearance and layout"""
        # Configure the main frame
        self.configure(corner_radius=0)
        
        # Configure tab bar
        self._segmented_button.configure(
            fg_color="#252526",
            selected_color="#1e1e1e",
            selected_hover_color="#1e1e1e",
            unselected_color="#252526",
            unselected_hover_color="#2d2d2d",
            corner_radius=0,
            border_width=0,
            height=35
        )
        
        # Make tabs left-aligned and ensure content fills width
        self._segmented_button.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.grid_columnconfigure(0, weight=1)  # Make the column containing tabs expand
        self.grid_rowconfigure(1, weight=1)  # Make the content area expand vertically
        
        # Configure tab content area to fill entire width and height without gaps
        tab_view = self._segmented_button.master
        tab_view.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        tab_view.grid_columnconfigure(0, weight=1)
        tab_view.grid_rowconfigure(0, weight=1)
        
        # Remove internal padding and configure corner radius
        tab_view.configure(corner_radius=0)
        
        # Configure scrollbar style for all tabs
        style = ttk.Style()
        style.configure("VSCode.Vertical.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            width=10,
            arrowsize=0,
            relief="flat",
            borderwidth=0
        )
        style.configure("VSCode.Horizontal.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            width=10,
            arrowsize=0,
            relief="flat",
            borderwidth=0
        )
        
    def add(self, name: str) -> ctk.CTkFrame:
        """Add a new tab with VSCode-like styling"""
        if name in self._tab_dict:
            return self._tab_dict[name]
            
        tab = super().add(name)
        
        # Configure the new tab frame to fill entire width without gaps
        tab.grid(row=0, column=0, sticky="nsew")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.configure(corner_radius=0)
        
        tab_button = self._segmented_button._buttons_dict[name]
        
        # Configure the tab button
        tab_button.configure(
            width=200,  # Fixed width for tabs
            height=35,
            corner_radius=0,
            border_width=1,
            border_color="#191919",
            fg_color="#252526",
            text="",  # Clear text as we'll add our own label
            hover_color="#2d2d2d"
        )
        
        # Create a container for tab content
        container = ctk.CTkFrame(tab_button, fg_color="transparent", height=35)
        container.place(relx=0, rely=0, relwidth=1, relheight=1)
        container.grid_propagate(False)
        
        # Add label
        label = ctk.CTkLabel(
            container,
            text=name,
            text_color="#cccccc",
            font=("Segoe UI", 11),
            anchor="w"
        )
        label.grid(row=0, column=0, padx=(10, 25), sticky="w")
        
        # Add close button
        close_button = ctk.CTkButton(
            container,
            text="×",
            width=16,
            height=16,
            fg_color="transparent",
            hover_color="#333333",
            text_color="#cccccc",
            font=("Segoe UI", 13),
            corner_radius=0,
            command=lambda: self.delete(name)
        )
        close_button.grid(row=0, column=1, padx=(0, 5), sticky="e")
        
        # Configure grid
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        
        # Store references
        self._close_buttons[name] = (container, close_button)
        
        # Update appearances
        self._update_tab_appearances()
        
        return tab
        
    def delete(self, tab_name: str) -> None:
        """Delete a tab and handle cleanup"""
        if tab_name in self._close_buttons:
            container, _ = self._close_buttons[tab_name]
            container.destroy()
            del self._close_buttons[tab_name]
        
        current = self.get()
        tabs = list(self._tab_dict.keys())
        next_tab = None
        
        if tab_name == current and len(tabs) > 1:
            current_idx = tabs.index(tab_name)
            next_tab = tabs[current_idx - 1] if current_idx > 0 else tabs[current_idx + 1]
            
        super().delete(tab_name)
        
        if next_tab:
            self.set(next_tab)
            
        self._update_tab_appearances()
        
    def _update_tab_appearances(self):
        """Update the appearance of all tabs"""
        current = self.get()
        for name, button in self._segmented_button._buttons_dict.items():
            if name == current:
                button.configure(
                    fg_color="#1e1e1e",
                    border_width=1,
                    border_color="#007acc"  # Blue top border for active tab
                )
                if name in self._close_buttons:
                    container, _ = self._close_buttons[name]
                    for widget in container.winfo_children():
                        if isinstance(widget, ctk.CTkLabel):
                            widget.configure(text_color="#ffffff")
            else:
                button.configure(
                    fg_color="#252526",
                    border_width=1,
                    border_color="#191919"
                )
                if name in self._close_buttons:
                    container, _ = self._close_buttons[name]
                    for widget in container.winfo_children():
                        if isinstance(widget, ctk.CTkLabel):
                            widget.configure(text_color="#cccccc")

class VSCodeTextEditor(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#1e1e1e")
        
        # Configure grid weights for proper expansion
        self.grid_columnconfigure(2, weight=1)  # Text widget column should expand
        self.grid_rowconfigure(0, weight=1)     # Row should expand vertically
        
        # Create text widget with line numbers
        self.line_numbers = tk.Text(
            self,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            highlightthickness=0,  # Remove border
            background='#1e1e1e',
            foreground='#858585',
            font=('Cascadia Code', 11),
            state='disabled',
            cursor='arrow'
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns", padx=0, pady=0)
        
        # Create main text widget
        self.text = tk.Text(
            self,
            wrap='none',
            border=0,
            highlightthickness=0,  # Remove border
            background='#1e1e1e',
            foreground='#d4d4d4',
            insertbackground='#aeafad',
            insertwidth=2,
            selectbackground='#264f78',
            selectforeground='#ffffff',
            font=('Cascadia Code', 11),
            undo=True,
            maxundo=-1,
            padx=5,
            pady=0  # Remove vertical padding
        )
        self.text.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        
        # Create scrollbars with VSCode style
        self.vsb = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.on_scroll_both,
            style="VSCode.Vertical.TScrollbar"
        )
        self.vsb.grid(row=0, column=3, sticky="ns")
        
        self.hsb = ttk.Scrollbar(
            self,
            orient='horizontal',
            command=self.text.xview,
            style="VSCode.Horizontal.TScrollbar"
        )
        self.hsb.grid(row=1, column=2, sticky="ew")
        
        # Configure text widget scrolling
        self.text.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set
        )
        
        # Configure grid weights
        self.grid_columnconfigure(2, weight=1)  # Make text widget expand horizontally
        self.grid_rowconfigure(0, weight=1)     # Make text widget expand vertically
        
        # Configure scrollbar style
        style = ttk.Style()
        style.configure("VSCode.Vertical.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            width=10,
            arrowsize=0,
            relief="flat",
            borderwidth=0
        )
        style.configure("VSCode.Horizontal.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            width=10,
            arrowsize=0,
            relief="flat",
            borderwidth=0
        )
        
        # Bind events
        self.text.bind('<Key>', self.on_key_press)
        self.text.bind('<Button-1>', self.on_click)
        self.text.bind('<ButtonRelease-1>', self.on_click)
        self.text.bind('<Control-plus>', self.increase_font)
        self.text.bind('<Control-minus>', self.decrease_font)
        self.text.bind('<<Modified>>', self.on_text_modified)
        
        # Initial line numbers
        self.update_line_numbers()
        self.text.edit_modified(False)  # Reset modified flag
        
    def on_scroll_both(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)
        
    def update_line_numbers(self):
        line_count = self.text.get('1.0', 'end').count('\n')
        if line_count == 0:
            line_count = 1
        line_numbers_text = '\n'.join(str(i).rjust(4) for i in range(1, line_count + 1))
        self.line_numbers.configure(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.configure(state='disabled')
        
    def on_key_press(self, event=None):
        self.update_line_numbers()
        self.update_cursor_position()
        
    def on_click(self, event=None):
        self.update_cursor_position()
        
    def update_cursor_position(self):
        try:
            pos = self.text.index('insert').split('.')
            line, col = int(pos[0]), int(pos[1]) + 1
            app = self.winfo_toplevel()
            if hasattr(app, 'status_bar'):
                app.status_bar.set_cursor_position(f"Ln {line}, Col {col}")
        except:
            pass
            
    def increase_font(self, event=None):
        current_size = self.text['font'].split()[-1]
        new_size = int(current_size) + 1
        self.text.configure(font=('Cascadia Code', new_size))
        self.line_numbers.configure(font=('Cascadia Code', new_size))
        
    def decrease_font(self, event=None):
        current_size = self.text['font'].split()[-1]
        new_size = max(6, int(current_size) - 1)
        self.text.configure(font=('Cascadia Code', new_size))
        self.line_numbers.configure(font=('Cascadia Code', new_size))
        
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text.delete('1.0', 'end')
                self.text.insert('1.0', content)
                self.update_line_numbers()
                self.update_cursor_position()
        except Exception as e:
            print(f"Error loading file: {e}")

    def on_text_modified(self, event):
        self.text.edit_modified(True)

class MinuxApp(ctk.CTk):
    def show_error_notification(self, message):
        """Display error message in notification bar"""
        logger.debug(f"Showing error notification: {message}")
        self.notification_label.configure(text=message)
        self.notification_frame.grid()
        
    def hide_notification(self):
        """Hide the notification bar"""
        logger.debug("Hiding notification")
        self.notification_frame.grid_remove()

    def __init__(self):
        try:
            logger.debug("Starting MinuxApp initialization")
            super().__init__()
            
            # Initialize tooltip variables
            self.tooltip_window = None
            self.tooltip_timer = None
            
            # Track current active panel
            self.current_panel = None
            
            # Set window title and size
            self.title("Marcetux")
            self.geometry("1200x800")
            
            # Set app icon
            try:
                app_icon = Image.open("media/icons/marcetux.png")
                self.iconphoto(True, ImageTk.PhotoImage(app_icon))
            except Exception as e:
                logger.error(f"Failed to load Marcetux icon: {str(e)}")
                # Try fallback icon
                try:
                    app_icon = Image.open("media/icons/app.png")
                    self.iconphoto(True, ImageTk.PhotoImage(app_icon))
                except Exception as e:
                    logger.error(f"Failed to load fallback icon: {str(e)}")

            # Create notification frame first (above status bar)
            logger.debug("Creating notification frame")
            self.notification_frame = ctk.CTkFrame(self, fg_color="#FF4444", height=30, corner_radius=0)
            self.notification_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
            self.notification_frame.grid_remove()  # Hidden by default
            
            # Add notification label
            self.notification_label = ctk.CTkLabel(
                self.notification_frame,
                text="",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=12)
            )
            self.notification_label.pack(side="left", padx=10)
            
            # Add error icon
            self.error_icon_label = ctk.CTkLabel(
                self.notification_frame,
                text="⚠",  # Error icon
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=14)
            )
            self.error_icon_label.pack(side="left", padx=(10, 5))
            
            # Add close button
            self.close_notification_button = ctk.CTkButton(
                self.notification_frame,
                text="×",
                width=20,
                height=20,
                fg_color="transparent",
                hover_color="#FF6666",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=14),
                command=self.hide_notification,
                corner_radius=0
            )
            self.close_notification_button.pack(side="right", padx=5)

            # Create main menu bar
            self.menu_bar = tk.Menu(self)
            self.configure(menu=self.menu_bar)

            # File menu
            self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="File", menu=self.file_menu)
            self.file_menu.add_command(label="New File", command=self.new_file)
            self.file_menu.add_command(label="New Window", command=lambda: MinuxApp())
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Open File...", command=lambda: self.open_file(None))
            self.file_menu.add_command(label="Open Folder...", command=lambda: self.open_folder(None))
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Save", command=self.save_current)
            self.file_menu.add_command(label="Save All", command=self.save_all)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Preferences", command=self.show_preferences)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Close Editor", command=self.close_current)
            self.file_menu.add_command(label="Close Window", command=self.quit)

            # Edit menu
            self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
            self.edit_menu.add_command(label="Undo", command=self.undo)
            self.edit_menu.add_command(label="Redo", command=self.redo)
            self.edit_menu.add_separator()
            self.edit_menu.add_command(label="Cut", command=self.cut)
            self.edit_menu.add_command(label="Copy", command=self.copy)
            self.edit_menu.add_command(label="Paste", command=self.paste)
            self.edit_menu.add_separator()
            self.edit_menu.add_command(label="Find", command=self.find)
            self.edit_menu.add_command(label="Replace", command=self.replace)

            # View menu
            self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="View", menu=self.view_menu)
            self.view_menu.add_command(label="Command Palette...", command=self.show_command_palette)
            self.view_menu.add_separator()
            self.view_menu.add_command(label="Welcome", command=self.show_welcome)
            self.view_menu.add_command(label="Minux Terminal", command=self.show_minux_terminal)
            self.view_menu.add_separator()
            self.view_menu.add_command(label="Explorer", command=self.toggle_explorer)
            self.view_menu.add_command(label="Search", command=self.toggle_search)
            self.view_menu.add_command(label="Source Control", command=self.toggle_source_control)
            self.view_menu.add_command(label="Debug", command=self.toggle_debug)
            self.view_menu.add_command(label="Extensions", command=self.toggle_extensions)
            self.view_menu.add_separator()
            self.view_menu.add_command(label="Terminal", command=self.toggle_terminal)
            self.view_menu.add_command(label="Problems", command=self.toggle_problems)
            self.view_menu.add_command(label="Output", command=self.toggle_output)
            self.view_menu.add_command(label="Debug Console", command=self.toggle_debug_console)

            # Run menu
            self.run_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
            self.run_menu.add_command(label="Start Debugging", command=self.start_debugging)
            self.run_menu.add_command(label="Run Without Debugging", command=self.run_without_debugging)
            self.run_menu.add_separator()
            self.run_menu.add_command(label="Toggle Breakpoint", command=self.toggle_breakpoint)

            # Terminal menu
            self.terminal_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Terminal", menu=self.terminal_menu)
            self.terminal_menu.add_command(label="New Terminal", command=self.new_terminal)
            self.terminal_menu.add_command(label="Split Terminal", command=self.split_terminal)
            self.terminal_menu.add_separator()
            self.terminal_menu.add_command(label="Run Task...", command=self.run_task)
            self.terminal_menu.add_command(label="Run Build Task...", command=self.run_build_task)

            # Help menu
            self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
            self.help_menu.add_command(label="Get Started", command=self.show_getting_started)
            self.help_menu.add_command(label="Documentation", command=self.show_documentation)
            self.help_menu.add_command(label="Tips and Tricks", command=self.show_tips)
            self.help_menu.add_separator()
            self.help_menu.add_command(label="About", command=self.show_about)

            # Configure main grid layout
            self.grid_columnconfigure(0, weight=0)  # Activity bar - fixed width
            self.grid_columnconfigure(1, weight=0)  # Sidebar - fixed width
            self.grid_columnconfigure(2, weight=1)  # Main content - should expand
            self.grid_rowconfigure(0, weight=1)     # Main content area should expand
            self.grid_rowconfigure(1, weight=0)     # Terminal area - fixed height
            self.grid_rowconfigure(2, weight=0)     # Notification area - fixed height
            self.grid_rowconfigure(3, weight=0)     # Status bar - fixed height

            # Create activity bar (leftmost)
            logger.debug("Creating activity bar")
            self.activity_bar = ctk.CTkFrame(self, fg_color="#333333", width=48, corner_radius=0)
            self.activity_bar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
            self.activity_bar.grid_propagate(False)

            # Create sidebar (left)
            logger.debug("Creating sidebar")
            self.sidebar = ctk.CTkFrame(self, fg_color="#252526", width=240, corner_radius=0)
            self.sidebar.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=0, pady=0)
            self.sidebar.grid_remove()  # Hidden by default
            self.sidebar.grid_propagate(False)  # Prevent sidebar from resizing

            # Create tab view (center)
            logger.debug("Creating tab view")
            self.tab_view = None
            try:
                self.tab_view = VSCodeTabview(self)
                self.tab_view.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
            except Exception as e:
                logger.error(f"Failed to create tab view: {str(e)}", exc_info=True)
                self.show_error_notification(f"Failed to create tab view: {str(e)}")
                raise
            
            if self.tab_view is None:
                raise ValueError("Failed to create tab view")
            
            # Create terminal panel (bottom)
            logger.debug("Creating terminal panel")
            self.terminal_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", height=200, corner_radius=0)
            self.terminal_frame.grid(row=1, column=2, sticky="ew")
            self.terminal_frame.grid_remove()  # Hide terminal by default
            self.terminal_frame.grid_propagate(False)
            self.terminal_visible = False
            
            # Create status bar (bottom)
            logger.debug("Creating status bar")
            self.status_bar = StatusBar(self)
            self.status_bar.grid(row=3, column=0, columnspan=3, sticky="ew")
            
            # Initialize database
            logger.debug("Initializing database")
            init_database()
            
            # Initialize UI components
            logger.debug("Setting up UI components")
            try:
                self.setup_activity_bar()
                self.setup_sidebar()
                self.setup_terminal()
                self.setup_status_bar()
            except Exception as e:
                logger.error(f"Failed to setup UI components: {str(e)}", exc_info=True)
                self.show_error_notification(f"Failed to setup UI components: {str(e)}")
                raise
            
            # Show welcome screen
            logger.debug("Attempting to show welcome screen")
            try:
                self.show_welcome()
            except Exception as e:
                logger.error(f"Failed to show welcome screen: {str(e)}", exc_info=True)
                self.show_error_notification(f"Failed to show welcome screen: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in MinuxApp initialization: {str(e)}", exc_info=True)
            if hasattr(self, 'show_error_notification'):
                self.show_error_notification(f"Failed to initialize application: {str(e)}")
            raise

    def handle_welcome_action(self, action):
        """Handle actions from the welcome screen"""
        if isinstance(action, tuple):
            action_type, task = action
            if action_type == "open":
                if os.path.isdir(task):
                    self.open_folder(task)
                else:
                    self.open_file(task)
            elif action_type == "open_todo":
                # Show the TODO list and highlight the selected task
                self.toggle_todo()
                self.show_todo_content()
                
                # Get the TODO tab frame and update it
                todo_frame = self.tab_view.tab("TODO")
                for widget in todo_frame.winfo_children():
                    widget.destroy()
                self.setup_todo_widget(todo_frame, selected_task=task)
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
        """Show getting started guide in a new tab"""
        try:
            # Create new Getting Started tab
            guide_frame = self.tab_view.add("Getting Started")
            guide_frame.configure(fg_color="#1e1e1e")
            
            # Create scrollable frame for content
            content = ctk.CTkScrollableFrame(
                guide_frame,
                fg_color="#1e1e1e",
                corner_radius=0
            )
            content.pack(fill="both", expand=True)
            
            # Add welcome content
            title = ctk.CTkLabel(
                content,
                text="Welcome to Minux!",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#cccccc"
            )
            title.pack(pady=(20, 10))
            
            # Quick start sections
            sections = [
                {
                    "title": "1. Create a New File",
                    "content": "Click File > New File or use Ctrl+N to create a new file."
                },
                {
                    "title": "2. Open Files and Folders",
                    "content": "Use File > Open to open existing files or folders."
                },
                {
                    "title": "3. Using the Terminal",
                    "content": "Toggle the integrated terminal using View > Terminal or Ctrl+`."
                },
                {
                    "title": "4. Managing Tasks",
                    "content": "Use the TODO feature to create and manage your tasks."
                },
                {
                    "title": "5. Customizing Minux",
                    "content": "Open Settings to customize your editor preferences."
                }
            ]
            
            for section in sections:
                # Section title
                section_title = ctk.CTkLabel(
                    content,
                    text=section["title"],
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#cccccc",
                    anchor="w"
                )
                section_title.pack(fill="x", pady=(20, 5), padx=20)
                
                # Section content
                section_content = ctk.CTkLabel(
                    content,
                    text=section["content"],
                    font=ctk.CTkFont(size=13),
                    text_color="#cccccc",
                    anchor="w",
                    wraplength=600,
                    justify="left"
                )
                section_content.pack(fill="x", pady=(0, 10), padx=20)
            
            # Switch to getting started tab
            self.tab_view.set("Getting Started")
            
        except Exception as e:
            logger.error(f"Failed to show getting started guide: {str(e)}")
            self.show_error_notification(f"Failed to show getting started guide: {str(e)}")

    def show_tips(self):
        """Show tips and tricks in a new tab"""
        try:
            # Create new Tips & Tricks tab
            tips_frame = self.tab_view.add("Tips & Tricks")
            tips_frame.configure(fg_color="#1e1e1e")
            
            # Create scrollable frame for content
            content = ctk.CTkScrollableFrame(
                tips_frame,
                fg_color="#1e1e1e",
                corner_radius=0
            )
            content.pack(fill="both", expand=True)
            
            # Add title
            title = ctk.CTkLabel(
                content,
                text="Tips & Tricks",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#cccccc"
            )
            title.pack(pady=(20, 10))
            
            # Tips sections
            tips = [
                {
                    "title": "Keyboard Shortcuts",
                    "items": [
                        "Ctrl+N: New File",
                        "Ctrl+O: Open File",
                        "Ctrl+S: Save File",
                        "Ctrl+W: Close Tab",
                        "Ctrl+`: Toggle Terminal"
                    ]
                },
                {
                    "title": "Editor Tips",
                    "items": [
                        "Use multiple cursors with Alt+Click",
                        "Quick file switching with Ctrl+Tab",
                        "Zoom in/out with Ctrl+/Ctrl-",
                        "Split editor with Ctrl+\\",
                        "Find in files with Ctrl+Shift+F"
                    ]
                },
                {
                    "title": "Terminal Tips",
                    "items": [
                        "Clear terminal with clear command",
                        "Split terminal for multiple sessions",
                        "Use tab completion for commands",
                        "Access command history with up/down arrows",
                        "Drag and drop files into terminal"
                    ]
                }
            ]
            
            for section in tips:
                # Section title
                section_title = ctk.CTkLabel(
                    content,
                    text=section["title"],
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#cccccc",
                    anchor="w"
                )
                section_title.pack(fill="x", pady=(20, 5), padx=20)
                
                # Tips list
                for item in section["items"]:
                    tip_label = ctk.CTkLabel(
                        content,
                        text="• " + item,
                        font=ctk.CTkFont(size=13),
                        text_color="#cccccc",
                        anchor="w",
                        wraplength=600,
                        justify="left"
                    )
                    tip_label.pack(fill="x", pady=(2, 2), padx=40)
            
            # Switch to tips tab
            self.tab_view.set("Tips & Tricks")
            
        except Exception as e:
            logger.error(f"Failed to show tips: {str(e)}")
            self.show_error_notification(f"Failed to show tips: {str(e)}")

    def clone_repository(self):
        """Show dialog to clone a git repository"""
        # TODO: Implement repository cloning
        pass

    def show_preferences(self):
        """Show preferences in a new tab"""
        try:
            # Check if Preferences tab exists
            if "Preferences" in self.tab_view._tab_dict:
                # Focus existing Preferences tab
                self.tab_view.set("Preferences")
                return

            # Create new Preferences tab
            pref_frame = self.tab_view.add("Preferences")
            pref_frame.configure(fg_color="#1e1e1e")
            
            # Create main container that fills the entire tab
            main_container = ctk.CTkFrame(pref_frame, fg_color="#1e1e1e", corner_radius=0)
            main_container.pack(fill="both", expand=True)
            
            # Create tabs
            tabview = ctk.CTkTabview(main_container, fg_color="#1e1e1e", corner_radius=0)
            tabview.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add tabs
            editor_tab = tabview.add("Editor")
            appearance_tab = tabview.add("Appearance")
            terminal_tab = tabview.add("Terminal")
            
            # Editor settings
            editor_frame = ctk.CTkFrame(editor_tab, fg_color="#1e1e1e", corner_radius=0)
            editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(editor_frame, text="Font Size").pack(anchor="w", padx=10, pady=5)
            font_size = ctk.CTkComboBox(editor_frame, values=["10", "11", "12", "14", "16", "18", "20"])
            font_size.pack(anchor="w", padx=10, pady=5, fill="x")
            
            ctk.CTkLabel(editor_frame, text="Tab Size").pack(anchor="w", padx=10, pady=5)
            tab_size = ctk.CTkComboBox(editor_frame, values=["2", "4", "6", "8"])
            tab_size.pack(anchor="w", padx=10, pady=5, fill="x")
            
            word_wrap = ctk.CTkCheckBox(editor_frame, text="Word Wrap")
            word_wrap.pack(anchor="w", padx=10, pady=10)
            
            # Appearance settings
            appearance_frame = ctk.CTkFrame(appearance_tab, fg_color="#1e1e1e", corner_radius=0)
            appearance_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(appearance_frame, text="Theme").pack(anchor="w", padx=10, pady=5)
            theme = ctk.CTkComboBox(appearance_frame, values=["Dark", "Light", "System"])
            theme.pack(anchor="w", padx=10, pady=5, fill="x")
            
            ctk.CTkLabel(appearance_frame, text="Color Scheme").pack(anchor="w", padx=10, pady=5)
            color_scheme = ctk.CTkComboBox(appearance_frame, values=["Default Dark+", "Monokai", "Solarized Dark", "GitHub Dark"])
            color_scheme.pack(anchor="w", padx=10, pady=5, fill="x")
            
            # Terminal settings
            terminal_frame = ctk.CTkFrame(terminal_tab, fg_color="#1e1e1e", corner_radius=0)
            terminal_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(terminal_frame, text="Font Family").pack(anchor="w", padx=10, pady=5)
            terminal_font = ctk.CTkComboBox(terminal_frame, values=["Cascadia Code", "Consolas", "Courier New", "Monospace"])
            terminal_font.pack(anchor="w", padx=10, pady=5, fill="x")
            
            ctk.CTkLabel(terminal_frame, text="Font Size").pack(anchor="w", padx=10, pady=5)
            terminal_font_size = ctk.CTkComboBox(terminal_frame, values=["10", "11", "12", "14", "16", "18", "20"])
            terminal_font_size.pack(anchor="w", padx=10, pady=5, fill="x")
            
            # Add Apply button at the bottom
            button_frame = ctk.CTkFrame(main_container, fg_color="#1e1e1e", corner_radius=0)
            button_frame.pack(fill="x", padx=10, pady=10)
            
            apply_button = ctk.CTkButton(
                button_frame,
                text="Apply Changes",
                command=lambda: self.apply_preferences(
                    font_size.get(),
                    tab_size.get(),
                    word_wrap.get(),
                    theme.get(),
                    color_scheme.get(),
                    terminal_font.get(),
                    terminal_font_size.get()
                )
            )
            apply_button.pack(side="right", padx=5)
            
            # Switch to the preferences tab
            self.tab_view.set("Preferences")
            
        except Exception as e:
            logger.error(f"Error showing preferences: {str(e)}")
            self.show_error_notification(f"Error showing preferences: {str(e)}")
            
    def apply_preferences(self, font_size, tab_size, word_wrap, theme, color_scheme, terminal_font, terminal_font_size):
        """Apply the selected preferences"""
        try:
            # TODO: Save preferences to config file
            logger.info("Applying preferences...")
            logger.info(f"Font Size: {font_size}")
            logger.info(f"Tab Size: {tab_size}")
            logger.info(f"Word Wrap: {word_wrap}")
            logger.info(f"Theme: {theme}")
            logger.info(f"Color Scheme: {color_scheme}")
            logger.info(f"Terminal Font: {terminal_font}")
            logger.info(f"Terminal Font Size: {terminal_font_size}")
            
            # Apply some settings immediately
            if hasattr(self, 'terminal'):
                self.terminal._textbox.configure(font=(terminal_font, int(terminal_font_size)))
                
        except Exception as e:
            logger.error(f"Error applying preferences: {str(e)}")
            
    def setup_activity_bar(self):
        """Setup the activity bar with icons and actions"""
        logger.debug("Setting up activity bar")
        
        # Load icons
        try:
            self.icons = {
                "files": ctk.CTkImage(
                    light_image=Image.open("media/icons/files.png"),
                    dark_image=Image.open("media/icons/files.png"),
                    size=(24, 24)
                ),
                "search": ctk.CTkImage(
                    light_image=Image.open("media/icons/search.png"),
                    dark_image=Image.open("media/icons/search.png"),
                    size=(24, 24)
                ),
                "git": ctk.CTkImage(
                    light_image=Image.open("media/icons/git.png"),
                    dark_image=Image.open("media/icons/git.png"),
                    size=(24, 24)
                ),
                "debug": ctk.CTkImage(
                    light_image=Image.open("media/icons/debug.png"),
                    dark_image=Image.open("media/icons/debug.png"),
                    size=(24, 24)
                ),
                "extensions": ctk.CTkImage(
                    light_image=Image.open("media/icons/extensions.png"),
                    dark_image=Image.open("media/icons/extensions.png"),
                    size=(24, 24)
                ),
                "settings": ctk.CTkImage(
                    light_image=Image.open("media/icons/settings.png"),
                    dark_image=Image.open("media/icons/settings.png"),
                    size=(24, 24)
                )
            }
            
            # Set app icon
            app_icon = Image.open("media/icons/app.png")
            self.iconphoto(True, ImageTk.PhotoImage(app_icon))
            
        except Exception as e:
            logger.error(f"Failed to load icons: {str(e)}")
            # Fallback to text icons if image loading fails
            self.icons = {
                "files": "📁",
                "search": "🔍",
                "git": "⑂",
                "debug": "⊳",
                "extensions": "⧉",
                "settings": "⚙"
            }
        
        # Create buttons for each action in VSCode order
        actions = [
            ("Explorer", self.icons["files"], self.toggle_explorer),  # File explorer first
            ("Search", self.icons["search"], self.toggle_search),
            ("Source Control", self.icons["git"], self.toggle_source_control),
            ("Run and Debug", self.icons["debug"], self.toggle_debug),
            ("Extensions", self.icons["extensions"], self.toggle_extensions),
            ("Settings", self.icons["settings"], self.show_preferences)
        ]
        
        # Clear any existing buttons
        for widget in self.activity_bar.winfo_children():
            widget.destroy()
            
        for i, (name, icon, command) in enumerate(actions):
            btn = ctk.CTkButton(
                self.activity_bar,
                text="" if isinstance(icon, ctk.CTkImage) else icon,
                image=icon if isinstance(icon, ctk.CTkImage) else None,
                width=48,
                height=48,
                fg_color="transparent",
                hover_color="#404040",
                text_color="#858585",
                font=ctk.CTkFont(size=16),
                command=command,
                corner_radius=0
            )
            btn.grid(row=i, column=0, sticky="ew")
            
            # Add tooltip
            self.create_tooltip(btn, name)
            
        # Configure grid
        self.activity_bar.grid_columnconfigure(0, weight=1)
        
    def setup_sidebar(self):
        """Setup the sidebar content"""
        logger.debug("Setting up sidebar")
        # Will be populated based on active activity bar item
        pass
        
    def setup_terminal(self):
        """Setup the terminal panel"""
        logger.debug("Setting up terminal")
        
        # Create terminal frame with title bar
        self.terminal_header = ctk.CTkFrame(self.terminal_frame, fg_color="#2D2D2D", height=35, corner_radius=0)
        self.terminal_header.pack(fill="x", side="top", padx=0, pady=0)
        self.terminal_header.pack_propagate(False)
        
        # Create header container for title and close button
        header_container = ctk.CTkFrame(self.terminal_header, fg_color="transparent")
        header_container.pack(fill="x", expand=True)
        
        # Add TERMINAL text
        self.terminal_title = ctk.CTkLabel(
            header_container,
            text="TERMINAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#BBBBBB"
        )
        self.terminal_title.pack(side="left", padx=10, pady=0)
        
        # Add close button
        close_button = ctk.CTkButton(
            header_container,
            text="×",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#404040",
            text_color="#BBBBBB",
            font=ctk.CTkFont(size=14),
            corner_radius=0,
            command=self.toggle_terminal
        )
        close_button.pack(side="right", padx=5, pady=0)
        
        # Create terminal text widget with proper styling
        self.terminal = ctk.CTkTextbox(
            self.terminal_frame,
            fg_color="#1e1e1e",
            text_color="#cccccc",
            font=("Cascadia Code", 11),
            wrap="none",
            corner_radius=0
        )
        self.terminal.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Configure text widget for logging
        self.terminal._textbox.configure(
            background="#1e1e1e",
            foreground="#cccccc",
            insertbackground="#cccccc",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=5,
            pady=5
        )
        
        # Configure scrollbar style
        style = ttk.Style()
        style.configure("VSCode.Vertical.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            width=10,
            arrowsize=0,
            relief="flat",
            borderwidth=0
        )
        
        # Configure terminal scrollbar
        if hasattr(self.terminal, '_scrollbar'):
            self.terminal._scrollbar.configure(style="VSCode.Vertical.TScrollbar")
        
        # Add terminal handler to logger with proper formatting
        terminal_handler = TerminalHandler(self.terminal)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        terminal_handler.setFormatter(formatter)
        logger.addHandler(terminal_handler)
        
        # Log some initial information
        logger.info("Terminal initialized")
        logger.debug("Debug logging enabled")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Working directory: {os.getcwd()}")
        
    def setup_status_bar(self):
        """Setup the status bar"""
        logger.debug("Setting up status bar")
        # Status bar is already created and configured in __init__
        pass
        
    def toggle_explorer(self):
        """Toggle the file explorer sidebar"""
        if self.sidebar.winfo_ismapped() and self.current_panel == "explorer":
            # If explorer is currently shown, hide it
            self.sidebar.grid_remove()
            self.current_panel = None
        else:
            # Show explorer
            self.sidebar.grid()
            # Clear existing content
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            # Add file explorer
            explorer = FileExplorer(self.sidebar, self)
            explorer.pack(fill="both", expand=True)
            self.current_panel = "explorer"
            
    def toggle_search(self):
        """Toggle the search sidebar"""
        if self.sidebar.winfo_ismapped() and self.current_panel == "search":
            # If search is currently shown, hide it
            self.sidebar.grid_remove()
            self.current_panel = None
        else:
            # Show search
            self.sidebar.grid()
            # Clear existing content
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            # TODO: Add search content
            search_label = ctk.CTkLabel(self.sidebar, text="Search", font=("Segoe UI", 14, "bold"))
            search_label.pack(padx=10, pady=10)
            self.current_panel = "search"
            
    def toggle_source_control(self):
        """Toggle the source control sidebar"""
        if self.sidebar.winfo_ismapped() and self.current_panel == "source_control":
            # If source control is currently shown, hide it
            self.sidebar.grid_remove()
            self.current_panel = None
        else:
            # Show source control
            self.sidebar.grid()
            # Clear existing content
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            # TODO: Add source control content
            git_label = ctk.CTkLabel(self.sidebar, text="Source Control", font=("Segoe UI", 14, "bold"))
            git_label.pack(padx=10, pady=10)
            self.current_panel = "source_control"
            
    def toggle_debug(self):
        """Toggle the debug sidebar"""
        if self.sidebar.winfo_ismapped() and self.current_panel == "debug":
            # If debug is currently shown, hide it
            self.sidebar.grid_remove()
            self.current_panel = None
        else:
            # Show debug
            self.sidebar.grid()
            # Clear existing content
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            # TODO: Add debug content
            debug_label = ctk.CTkLabel(self.sidebar, text="Run and Debug", font=("Segoe UI", 14, "bold"))
            debug_label.pack(padx=10, pady=10)
            self.current_panel = "debug"
            
    def toggle_extensions(self):
        """Toggle the extensions sidebar"""
        if self.sidebar.winfo_ismapped() and self.current_panel == "extensions":
            # If extensions is currently shown, hide it
            self.sidebar.grid_remove()
            self.current_panel = None
        else:
            # Show extensions
            self.sidebar.grid()
            # Clear existing content
            for widget in self.sidebar.winfo_children():
                widget.destroy()
            # TODO: Add extensions content
            extensions_label = ctk.CTkLabel(self.sidebar, text="Extensions", font=("Segoe UI", 14, "bold"))
            extensions_label.pack(padx=10, pady=10)
            self.current_panel = "extensions"
            
    def toggle_terminal(self):
        """Toggle the terminal panel"""
        if self.terminal_visible:
            self.terminal_frame.grid_remove()
            self.terminal_visible = False
        else:
            # Configure terminal frame
            self.terminal_frame.grid(row=1, column=2, sticky="nsew", padx=0, pady=0)
            
            # Configure grid weights for proper expansion
            self.terminal_frame.grid_columnconfigure(0, weight=1)
            self.terminal_frame.grid_rowconfigure(1, weight=1)  # Row 0 is header, row 1 is terminal
            
            # Show terminal
            self.terminal_visible = True
            
            # Give focus to the terminal
            if hasattr(self, 'terminal'):
                self.terminal._textbox.focus_set()

    def open_file(self, file_path):
        """Open a file in a new tab"""
        try:
            # Get file name for tab title
            file_name = os.path.basename(file_path)
            
            # Create new tab
            tab = self.tab_view.add(file_name)
            
            # Create text editor in the tab
            editor = VSCodeTextEditor(tab)
            editor.pack(fill="both", expand=True)
            
            # Load file content
            editor.load_file(file_path)
            
            # Switch to the new tab
            self.tab_view.set(file_name)
            
        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {str(e)}")
            self.show_error_notification(f"Failed to open file: {str(e)}")

    def toggle_todo(self):
        """Toggle the TODO list tab"""
        if "TODO" in self.tab_view._tab_dict:
            # If TODO tab exists, just switch to it
            self.tab_view.set("TODO")
        else:
            # Create new TODO tab
            todo_frame = self.tab_view.add("TODO")
            self.setup_todo_widget(todo_frame)
            self.tab_view.set("TODO")
            
    def setup_todo_widget(self, frame, selected_task=None):
        """Setup the TODO widget in the given frame"""
        try:
            # Create TODO widget
            todo_widget = TodoWidget(
                frame,
                self.show_error_notification,
                DB_PATH,
                selected_task=selected_task
            )
            todo_widget.pack(fill="both", expand=True)
            
        except Exception as e:
            logger.error(f"Failed to setup TODO widget: {str(e)}")
            self.show_error_notification(f"Failed to setup TODO widget: {str(e)}")
            
    def show_todo_content(self):
        """Show TODO content in the sidebar"""
        # Clear existing content
        for widget in self.sidebar.winfo_children():
            widget.destroy()
            
        try:
            # Create TODO widget in sidebar
            todo_widget = TodoWidget(
                self.sidebar,
                self.show_error_notification,
                DB_PATH
            )
            todo_widget.pack(fill="both", expand=True)
            
            # Show sidebar if hidden
            if not self.sidebar.winfo_ismapped():
                self.sidebar.grid()
                
        except Exception as e:
            logger.error(f"Failed to show TODO content: {str(e)}")
            self.show_error_notification(f"Failed to show TODO content: {str(e)}")

    def new_file(self):
        """Create a new empty file"""
        tab = self.tab_view.add("untitled")
        editor = VSCodeTextEditor(tab)
        editor.pack(fill="both", expand=True)
        self.tab_view.set("untitled")

    def save_current(self):
        """Save the current file"""
        current = self.tab_view.get()
        if current:
            # TODO: Implement actual file saving
            self.show_error_notification("Save functionality coming soon")

    def save_all(self):
        """Save all open files"""
        # TODO: Implement saving all files
        self.show_error_notification("Save All functionality coming soon")

    def close_current(self):
        """Close the current editor"""
        current = self.tab_view.get()
        if current:
            self.tab_view.delete(current)

    def undo(self):
        """Undo last action in current editor"""
        current = self.tab_view.get()
        if current:
            tab = self.tab_view.tab(current)
            for widget in tab.winfo_children():
                if isinstance(widget, VSCodeTextEditor):
                    widget.text.edit_undo()

    def redo(self):
        """Redo last undone action in current editor"""
        current = self.tab_view.get()
        if current:
            tab = self.tab_view.tab(current)
            for widget in tab.winfo_children():
                if isinstance(widget, VSCodeTextEditor):
                    widget.text.edit_redo()

    def cut(self):
        """Cut selected text"""
        current = self.tab_view.get()
        if current:
            tab = self.tab_view.tab(current)
            for widget in tab.winfo_children():
                if isinstance(widget, VSCodeTextEditor):
                    widget.text.event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        current = self.tab_view.get()
        if current:
            tab = self.tab_view.tab(current)
            for widget in tab.winfo_children():
                if isinstance(widget, VSCodeTextEditor):
                    widget.text.event_generate("<<Copy>>")

    def paste(self):
        """Paste text from clipboard"""
        current = self.tab_view.get()
        if current:
            tab = self.tab_view.tab(current)
            for widget in tab.winfo_children():
                if isinstance(widget, VSCodeTextEditor):
                    widget.text.event_generate("<<Paste>>")

    def find(self):
        """Show find dialog"""
        # TODO: Implement find functionality
        self.show_error_notification("Find functionality coming soon")

    def replace(self):
        """Show replace dialog"""
        # TODO: Implement replace functionality
        self.show_error_notification("Replace functionality coming soon")

    def show_command_palette(self):
        """Show command palette"""
        # TODO: Implement command palette
        self.show_error_notification("Command Palette coming soon")

    def toggle_problems(self):
        """Toggle problems panel"""
        # TODO: Implement problems panel
        self.show_error_notification("Problems panel coming soon")

    def toggle_output(self):
        """Toggle output panel"""
        # TODO: Implement output panel
        self.show_error_notification("Output panel coming soon")

    def toggle_debug_console(self):
        """Toggle debug console"""
        # TODO: Implement debug console
        self.show_error_notification("Debug console coming soon")

    def start_debugging(self):
        """Start debugging session"""
        # TODO: Implement debugging
        self.show_error_notification("Debugging functionality coming soon")

    def run_without_debugging(self):
        """Run current file without debugging"""
        # TODO: Implement run without debugging
        self.show_error_notification("Run without debugging coming soon")

    def toggle_breakpoint(self):
        """Toggle breakpoint at current line"""
        # TODO: Implement breakpoint toggling
        self.show_error_notification("Breakpoint functionality coming soon")

    def new_terminal(self):
        """Create new terminal"""
        self.toggle_terminal()

    def split_terminal(self):
        """Split the terminal"""
        # TODO: Implement terminal splitting
        self.show_error_notification("Terminal splitting coming soon")

    def run_task(self):
        """Run a task"""
        # TODO: Implement task running
        self.show_error_notification("Task running coming soon")

    def run_build_task(self):
        """Run a build task"""
        # TODO: Implement build task running
        self.show_error_notification("Build task running coming soon")

    def show_about(self):
        """Show about dialog"""
        try:
            # Create about window
            about_window = ctk.CTkToplevel(self)
            about_window.title("About Minux")
            about_window.geometry("400x300")
            about_window.resizable(False, False)
            
            # Center the window
            about_window.update_idletasks()
            x = (about_window.winfo_screenwidth() - about_window.winfo_width()) // 2
            y = (about_window.winfo_screenheight() - about_window.winfo_height()) // 2
            about_window.geometry(f"+{x}+{y}")
            
            # Add content
            title = ctk.CTkLabel(
                about_window,
                text="Minux",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#cccccc"
            )
            title.pack(pady=(20, 5))
            
            version = ctk.CTkLabel(
                about_window,
                text="Version 1.0.0",
                font=ctk.CTkFont(size=12),
                text_color="#cccccc"
            )
            version.pack(pady=(0, 20))
            
            description = ctk.CTkLabel(
                about_window,
                text="A modern, customizable code editor\nbuilt with Python and CustomTkinter",
                font=ctk.CTkFont(size=13),
                text_color="#cccccc",
                wraplength=300,
                justify="center"
            )
            description.pack(pady=(0, 20))
            
            # Add close button
            close_button = ctk.CTkButton(
                about_window,
                text="Close",
                width=100,
                command=about_window.destroy
            )
            close_button.pack(pady=(20, 0))
            
        except Exception as e:
            logger.error(f"Failed to show about dialog: {str(e)}")
            self.show_error_notification(f"Failed to show about dialog: {str(e)}")

    def show_documentation(self):
        """Show documentation in a new tab"""
        try:
            # Create new Documentation tab
            doc_frame = self.tab_view.add("Documentation")
            doc_frame.configure(fg_color="#1e1e1e")
            
            # Create scrollable frame for content
            content = ctk.CTkScrollableFrame(
                doc_frame,
                fg_color="#1e1e1e",
                corner_radius=0
            )
            content.pack(fill="both", expand=True)
            
            # Add documentation content
            title = ctk.CTkLabel(
                content,
                text="Minux Documentation",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#cccccc"
            )
            title.pack(pady=(20, 10))
            
            sections = [
                {
                    "title": "Getting Started",
                    "content": "Welcome to Minux! This guide will help you get started with the basic features."
                },
                {
                    "title": "File Management",
                    "content": "Learn how to create, open, and save files in Minux."
                },
                {
                    "title": "Editor Features",
                    "content": "Discover powerful editing features including syntax highlighting and code completion."
                },
                {
                    "title": "Terminal Usage",
                    "content": "Work with the integrated terminal for command-line operations."
                },
                {
                    "title": "Task Management",
                    "content": "Use the TODO feature to manage your tasks efficiently."
                }
            ]
            
            for section in sections:
                # Section title
                section_title = ctk.CTkLabel(
                    content,
                    text=section["title"],
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#cccccc",
                    anchor="w"
                )
                section_title.pack(fill="x", pady=(20, 5), padx=20)
                
                # Section content
                section_content = ctk.CTkLabel(
                    content,
                    text=section["content"],
                    font=ctk.CTkFont(size=13),
                    text_color="#cccccc",
                    anchor="w",
                    wraplength=600,
                    justify="left"
                )
                section_content.pack(fill="x", pady=(0, 10), padx=20)
            
            # Switch to documentation tab
            self.tab_view.set("Documentation")
            
        except Exception as e:
            logger.error(f"Failed to show documentation: {str(e)}")
            self.show_error_notification(f"Failed to show documentation: {str(e)}")

    def show_welcome(self):
        """Show or focus the Welcome tab"""
        try:
            # Check if Welcome tab exists
            if "Welcome" in self.tab_view._tab_dict:
                # Focus existing Welcome tab
                self.tab_view.set("Welcome")
            else:
                # Create new Welcome tab
                welcome_frame = self.tab_view.add("Welcome")
                if welcome_frame is None:
                    raise ValueError("Failed to create welcome frame")
                
                # Configure welcome frame
                welcome_frame.configure(fg_color="#1e1e1e")
                welcome_frame.grid_columnconfigure(0, weight=1)
                welcome_frame.grid_rowconfigure(0, weight=1)
                
                # Create welcome screen
                welcome_screen = WelcomeScreen(welcome_frame, self.handle_welcome_action)
                welcome_screen.pack(fill="both", expand=True, padx=0, pady=0)
                
                # Switch to Welcome tab
                self.tab_view.set("Welcome")
                
        except Exception as e:
            logger.error(f"Failed to show Welcome tab: {str(e)}")
            self.show_error_notification(f"Failed to show Welcome tab: {str(e)}")

    def show_minux_terminal(self):
        """Show or focus the Minux Terminal tab"""
        try:
            # Check if Minux Terminal tab exists
            if "Minux Terminal" in self.tab_view._tab_dict:
                # Focus existing Minux Terminal tab
                self.tab_view.set("Minux Terminal")
            else:
                # Create new Minux Terminal tab
                terminal_frame = self.tab_view.add("Minux Terminal")
                terminal_frame.configure(fg_color="#1e1e1e")
                
                # Create terminal text widget
                terminal = ctk.CTkTextbox(
                    terminal_frame,
                    fg_color="#1e1e1e",
                    text_color="#cccccc",
                    font=("Cascadia Code", 11),
                    wrap="none",
                    corner_radius=0
                )
                terminal.pack(fill="both", expand=True)
                
                # Add terminal handler to logger
                terminal_handler = TerminalHandler(terminal)
                terminal_handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                )
                logger.addHandler(terminal_handler)
                
                # Switch to the terminal tab
                self.tab_view.set("Minux Terminal")
                
                # Log some initial information
                logger.info("Minux Terminal initialized")
                logger.info("Logging level: DEBUG")
                logger.info(f"Python version: {sys.version}")
                logger.info(f"Platform: {platform.platform()}")
                logger.info(f"Working directory: {os.getcwd()}")
                
        except Exception as e:
            logger.error(f"Failed to show Minux Terminal: {str(e)}")
            self.show_error_notification(f"Failed to show Minux Terminal: {str(e)}")

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            self.schedule_tooltip(widget, text)
            
        def leave(event):
            self.cancel_tooltip()
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def schedule_tooltip(self, widget, text):
        """Schedule the tooltip to appear after a delay"""
        self.cancel_tooltip()
        self.tooltip_timer = self.after(500, lambda: self.show_tooltip(widget, text))
        
    def cancel_tooltip(self):
        """Cancel the scheduled tooltip"""
        if self.tooltip_timer:
            self.after_cancel(self.tooltip_timer)
            self.tooltip_timer = None
            
    def show_tooltip(self, widget, text):
        """Show the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        self.tooltip_window = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, 
            text=text, 
            justify='left',
            background="#2A2D2E",
            foreground="#CCCCCC",
            relief='solid',
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack()

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
