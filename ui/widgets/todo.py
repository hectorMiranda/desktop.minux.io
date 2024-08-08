import customtkinter as ctk
from PIL import Image
import os
import tkinter as tk

class TodoWidget(ctk.CTkFrame):
    def _load_icon(self, icon_name, fallback_text):
        """Helper function to load an icon with a fallback"""
        try:
            icon_path = os.path.join("media", "icons", icon_name)
            if os.path.exists(icon_path):
                icon = ctk.CTkImage(
                    light_image=Image.open(icon_path),
                    dark_image=Image.open(icon_path),
                    size=(16, 16)
                )
                return icon
            else:
                if self.show_error_notification:
                    self.show_error_notification(f"Icon not found: {icon_path}")
                return fallback_text
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error loading {icon_name}: {e}")
            return fallback_text

    def __init__(self, parent, show_error_notification=None, db_path=None, selected_task=None):
        super().__init__(parent)
        
        # Store instance variables
        self.show_error_notification = show_error_notification
        self.db_path = db_path
        self.selected_task = selected_task
        
        # Create main frame
        self.todo_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=0)
        self.todo_frame.pack(fill="both", expand=True)

        # Create toolbar
        self.toolbar = ctk.CTkFrame(self.todo_frame, fg_color="#252526", corner_radius=0, height=40)
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)

        # Add title with icon
        todo_icon = self._load_icon("todo.png", "📝")
        if isinstance(todo_icon, ctk.CTkImage):
            title_label = ctk.CTkLabel(
                self.toolbar,
                text=" TODOS",
                image=todo_icon,
                compound="left",
                text_color="#cccccc",
                font=ctk.CTkFont(size=12, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                self.toolbar,
                text=f"{todo_icon} TODOS",
                text_color="#cccccc",
                font=ctk.CTkFont(size=12, weight="bold")
            )
        title_label.pack(side="left", padx=10)

        # Add view options on the right
        view_options = [
            ("List", "list.png", "📄", self.list_view),
            ("Tree", "tree.png", "🌳", self.tree_view),
            ("Board", "board.png", "📋", self.board_view)
        ]

        self.view_buttons = {}
        
        for text, icon_name, fallback, command in view_options:
            icon = self._load_icon(icon_name, fallback)
            if isinstance(icon, ctk.CTkImage):
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=text,
                    image=icon,
                    compound="left",
                    fg_color="transparent",
                    hover_color="#2a2d2e",
                    width=60,
                    height=30,
                    corner_radius=4,
                    command=command
                )
            else:
                btn = ctk.CTkButton(
                    self.toolbar,
                    text=f"{icon} {text}",
                    fg_color="transparent",
                    hover_color="#2a2d2e",
                    width=60,
                    height=30,
                    corner_radius=4,
                    command=command
                )
            btn.pack(side="right", padx=2)
            self.view_buttons[text] = btn

        # Create filter bar
        self.filter_bar = ctk.CTkFrame(self.todo_frame, fg_color="#252526", corner_radius=0, height=35)
        self.filter_bar.pack(fill="x")
        self.filter_bar.pack_propagate(False)

        # Add filter options
        filter_options = [
            ("All", self.show_all_tasks),
            ("Active", self.show_active_tasks),
            ("Completed", self.show_completed_tasks)
        ]

        self.filter_buttons = {}  # Store references to filter buttons
        
        for text, command in filter_options:
            btn = ctk.CTkButton(
                self.filter_bar,
                text=text,
                fg_color="transparent",
                hover_color="#2a2d2e",
                text_color="#cccccc",
                height=25,
                corner_radius=4,
                font=ctk.CTkFont(size=11),
                command=command
            )
            btn.pack(side="left", padx=5, pady=5)
            self.filter_buttons[text] = btn
        
        # Create content area
        self.content = ctk.CTkFrame(self.todo_frame, fg_color="#1e1e1e", corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add task entry with icon
        self.entry_frame = ctk.CTkFrame(self.content, fg_color="#3c3c3c", corner_radius=4)
        self.entry_frame.pack(fill="x")

        try:
            icon_path = os.path.join("media", "icons", "add.png")
            if os.path.exists(icon_path):
                self.task_icon = ctk.CTkImage(
                    light_image=Image.open(icon_path),
                    dark_image=Image.open(icon_path),
                    size=(16, 16)
                )
                icon_label = ctk.CTkLabel(
                    self.entry_frame,
                    text="",
                    image=self.task_icon,
                    width=16
                )
            else:
                icon_label = ctk.CTkLabel(
                    self.entry_frame,
                    text="+",
                    width=16,
                    font=ctk.CTkFont(size=16)
                )
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error loading add icon: {e}")
            icon_label = ctk.CTkLabel(
                self.entry_frame,
                text="+",
                width=16,
                font=ctk.CTkFont(size=16)
            )
        icon_label.pack(side="left", padx=8)
        
        self.task_entry = ctk.CTkEntry(
            self.entry_frame,
            placeholder_text="Add a task... (Press Enter to add)",
            height=35,
            corner_radius=4,
            fg_color="#3c3c3c",
            border_color="#3c3c3c",
            border_width=0,
            text_color="#cccccc"
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        
        # Create tasks list
        self.tasks_frame = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#424242",
            scrollbar_button_hover_color="#525252"
        )
        self.tasks_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Initialize empty tasks list and views
        self.tasks = []
        self.current_view = "list"  # Default view
        self.current_filter = "All"  # Default filter
        
        # Load tasks from database if available
        if self.db_path:
            self.load_tasks()
            
        # Highlight selected task if provided
        if self.selected_task:
            self.highlight_task(self.selected_task)
            
        # Update UI state
        self._update_view_buttons()
        self._update_filter_buttons()
        
        # Bind font scaling
        self.bind("<Control-plus>", self._increase_font_size)
        self.bind("<Control-minus>", self._decrease_font_size)
        self.bind("<Control-equal>", self._increase_font_size)  # For keyboards where + is on the = key
        
        # Initialize font size
        self.current_font_size = 12

    def _increase_font_size(self, event=None):
        """Increase font size for all elements"""
        self.current_font_size += 1
        self._update_fonts()
        
    def _decrease_font_size(self, event=None):
        """Decrease font size for all elements"""
        if self.current_font_size > 8:  # Don't go too small
            self.current_font_size -= 1
            self._update_fonts()
            
    def _update_fonts(self):
        """Update fonts for all elements"""
        # Update filter buttons
        for btn in self.filter_buttons.values():
            btn.configure(font=ctk.CTkFont(size=self.current_font_size))
            
        # Update view buttons
        for btn in self.view_buttons.values():
            btn.configure(font=ctk.CTkFont(size=self.current_font_size))
            
        # Update task entry
        self.task_entry.configure(font=ctk.CTkFont(size=self.current_font_size))
        
        # Update tasks
        for task in self.tasks:
            task["checkbox"].configure(font=ctk.CTkFont(size=self.current_font_size))

    def _update_view_buttons(self):
        """Update the visual state of view buttons"""
        for view_name, btn in self.view_buttons.items():
            if view_name.lower().startswith(self.current_view.lower()):
                btn.configure(fg_color="#37373d")
            else:
                btn.configure(fg_color="transparent")

    def _update_filter_buttons(self):
        """Update the visual state of filter buttons"""
        for filter_name, btn in self.filter_buttons.items():
            if filter_name == self.current_filter:
                btn.configure(fg_color="#37373d")
            else:
                btn.configure(fg_color="transparent")

    def show_all_tasks(self):
        """Show all tasks"""
        self.current_filter = "All"
        self._update_filter_buttons()
        for task in self.tasks:
            task["frame"].pack(fill="x", pady=(0, 2))

    def show_active_tasks(self):
        """Show only active (uncompleted) tasks"""
        self.current_filter = "Active"
        self._update_filter_buttons()
        for task in self.tasks:
            if not task["completed"].get():
                task["frame"].pack(fill="x", pady=(0, 2))
            else:
                task["frame"].pack_forget()

    def show_completed_tasks(self):
        """Show only completed tasks"""
        self.current_filter = "Completed"
        self._update_filter_buttons()
        for task in self.tasks:
            if task["completed"].get():
                task["frame"].pack(fill="x", pady=(0, 2))
            else:
                task["frame"].pack_forget()

    def tree_view(self):
        """Switch to tree view"""
        self.current_view = "tree"
        self._update_view_buttons()
        # Placeholder for tree view layout
        self.show_error_notification("Tree view is a placeholder")

    def list_view(self):
        """Switch to list view"""
        self.current_view = "list"
        self._update_view_buttons()
        self.refresh_view()

    def board_view(self):
        """Switch to board view"""
        self.current_view = "board"
        self._update_view_buttons()
        # Placeholder for board view layout
        self.show_error_notification("Board view is a placeholder")

    def refresh_view(self):
        """Refresh the current view"""
        for task in self.tasks:
            task["frame"].pack_forget()
        
        if self.current_view == "list":
            for task in self.tasks:
                task["frame"].pack(fill="x", pady=(0, 2))
    
    def load_tasks(self):
        """Load tasks from the database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tasks
            cursor.execute("SELECT task, done FROM todos ORDER BY created_date DESC")
            tasks = cursor.fetchall()
            
            # Add each task to the UI
            for task_text, done in tasks:
                self.add_task_to_ui(task_text, done)
                
            conn.close()
            
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error loading tasks: {e}")
    
    def add_task_to_ui(self, task_text, done=False):
        """Add a task to the UI with optional completion status"""
        # Create task frame
        task_frame = ctk.CTkFrame(
            self.tasks_frame,
            fg_color="transparent" if not done else "gray20",
            corner_radius=0,
            height=35
        )
        task_frame.pack(fill="x", pady=(0, 2))
        task_frame.pack_propagate(False)
        
        # Add checkbox
        var = ctk.BooleanVar(value=done)
        checkbox = ctk.CTkCheckBox(
            task_frame,
            text=task_text,
            variable=var,
            corner_radius=0,
            text_color="white" if not done else "gray50",
            command=lambda: self.toggle_task(checkbox, task_frame)
        )
        checkbox.pack(side="left", padx=5)
        
        # Add delete button
        try:
            self.delete_image = ctk.CTkImage(
                light_image=Image.open("media/icons/close.png"),
                dark_image=Image.open("media/icons/close.png"),
                size=(12, 12)
            )
            delete_btn = ctk.CTkButton(
                task_frame,
                text="",
                image=self.delete_image,
                width=20,
                height=20,
                corner_radius=0,
                fg_color="transparent",
                hover_color="#333333",
                command=lambda: self.delete_task(task_frame, task_text)
            )
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error loading delete icon: {e}")
            delete_btn = ctk.CTkButton(
                task_frame,
                text="×",
                width=20,
                height=20,
                corner_radius=0,
                fg_color="transparent",
                hover_color="#333333",
                command=lambda: self.delete_task(task_frame, task_text)
            )
        delete_btn.pack(side="right", padx=5)
        
        # Add task to list
        self.tasks.append({
            "frame": task_frame,
            "checkbox": checkbox,
            "delete": delete_btn,
            "completed": var,
            "text": task_text
        })
    
    def add_task(self):
        """Add a new task"""
        task_text = self.task_entry.get().strip()
        if task_text:
            try:
                if self.db_path:
                    # Add to database
                    import sqlite3
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO todos (task) VALUES (?)", (task_text,))
                    conn.commit()
                    conn.close()
                
                # Add to UI
                self.add_task_to_ui(task_text)
                
                # Clear entry
                self.task_entry.delete(0, "end")
                
            except Exception as e:
                if self.show_error_notification:
                    self.show_error_notification(f"Error adding task: {e}")
    
    def toggle_task(self, checkbox, task_frame):
        """Toggle task completion status"""
        try:
            is_completed = checkbox.get()
            task_text = checkbox.cget("text")
            
            if self.db_path:
                # Update database
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE todos SET done = ?, completed_date = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END WHERE task = ?",
                    (is_completed, is_completed, task_text)
                )
                conn.commit()
                conn.close()
            
            # Update UI
            if is_completed:
                checkbox.configure(text_color="gray50")
                task_frame.configure(fg_color="gray20")
            else:
                checkbox.configure(text_color="white")
                task_frame.configure(fg_color="transparent")
                
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error toggling task: {e}")
    
    def delete_task(self, task_frame, task_text):
        """Delete a task"""
        try:
            if self.db_path:
                # Delete from database
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM todos WHERE task = ?", (task_text,))
                conn.commit()
                conn.close()
            
            # Remove from UI
            for task in self.tasks:
                if task["frame"] == task_frame:
                    self.tasks.remove(task)
                    task_frame.destroy()
                    break
                    
        except Exception as e:
            if self.show_error_notification:
                self.show_error_notification(f"Error deleting task: {e}")
    
    def highlight_task(self, task_text):
        """Highlight a specific task"""
        for task in self.tasks:
            if task["text"] == task_text:
                task["frame"].configure(fg_color="#264f78")
                self.after(2000, lambda: task["frame"].configure(
                    fg_color="gray20" if task["completed"].get() else "transparent"
                ))
                break 

    def _focus_task_entry(self):
        """Focus the task entry field"""
        self.task_entry.focus_set()

    def _save_tasks(self):
        """Save all tasks to the database"""
        if self.db_path:
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # First, get all tasks from the database
                cursor.execute("SELECT task FROM todos")
                db_tasks = set(task[0] for task in cursor.fetchall())
                
                # Get current tasks from UI
                ui_tasks = set(task["text"] for task in self.tasks)
                
                # Add new tasks
                for task_text in ui_tasks - db_tasks:
                    cursor.execute("INSERT INTO todos (task) VALUES (?)", (task_text,))
                
                # Remove deleted tasks
                for task_text in db_tasks - ui_tasks:
                    cursor.execute("DELETE FROM todos WHERE task = ?", (task_text,))
                
                conn.commit()
                conn.close()
                
                if self.show_error_notification:
                    self.show_error_notification("Tasks saved successfully")
                    
            except Exception as e:
                if self.show_error_notification:
                    self.show_error_notification(f"Error saving tasks: {e}")
        else:
            if self.show_error_notification:
                self.show_error_notification("No database configured for saving tasks") 