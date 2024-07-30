import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=22, fg_color="#007ACC", **kwargs)
        self.grid_propagate(False)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Make the middle section expand
        
        # Left section
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="w", padx=(5, 0))
        
        # Source control info
        self.branch_label = self._create_status_item("main", "🔄")
        self.errors_label = self._create_status_item("0", "⚠️")
        self.warnings_label = self._create_status_item("0", "⚡")
        
        # Middle section (for notifications)
        self.middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_frame.grid(row=0, column=1, sticky="ew")
        
        self.notification_label = ctk.CTkLabel(
            self.middle_frame,
            text="",
            text_color="#FFFFFF",
            fg_color="transparent"
        )
        self.notification_label.grid(row=0, column=0, padx=5)
        
        # Right section
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=2, sticky="e", padx=(0, 5))
        
        # Editor info
        self.encoding_label = self._create_clickable_item("UTF-8")
        self.line_ending_label = self._create_clickable_item("LF")
        self.file_type_label = self._create_clickable_item("Python")
        self.cursor_pos_label = self._create_clickable_item("Ln 1, Col 1")
        self.spaces_label = self._create_clickable_item("Spaces: 4")
        
    def _create_status_item(self, text, icon=None):
        frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame.pack(side="left", padx=5)
        
        if icon:
            icon_label = ctk.CTkLabel(frame, text=icon, text_color="#FFFFFF")
            icon_label.pack(side="left", padx=(0, 2))
            
        label = ctk.CTkLabel(frame, text=text, text_color="#FFFFFF")
        label.pack(side="left")
        return label
        
    def _create_clickable_item(self, text):
        btn = ctk.CTkButton(
            self.right_frame,
            text=text,
            fg_color="transparent",
            hover_color="#1E8AD1",
            height=22,
            corner_radius=0,
            command=lambda t=text: self._handle_click(t)
        )
        btn.pack(side="left")
        return btn
        
    def _handle_click(self, item_type):
        # Handle clicks on status bar items
        pass
        
    def update_cursor_position(self, line, column):
        """Update the cursor position display"""
        self.cursor_pos_label.configure(text=f"Ln {line}, Col {column}")
        
    def update_file_type(self, file_type):
        """Update the file type display"""
        self.file_type_label.configure(text=file_type)
        
    def update_encoding(self, encoding):
        """Update the encoding display"""
        self.encoding_label.configure(text=encoding)
        
    def update_line_ending(self, line_ending):
        """Update the line ending display"""
        self.line_ending_label.configure(text=line_ending)
        
    def update_spaces(self, spaces):
        """Update the spaces display"""
        self.spaces_label.configure(text=f"Spaces: {spaces}")
        
    def set_warning_count(self, count):
        """Update the warning count"""
        self.warnings_label.configure(text=str(count))
        
    def set_error_count(self, count):
        """Update the error count"""
        self.errors_label.configure(text=str(count))
        
    def set_branch(self, branch):
        """Update the git branch display"""
        self.branch_label.configure(text=branch)
        
    def show_notification(self, message, duration=3000):
        """Show a temporary notification in the status bar"""
        self.notification_label.configure(text=message)
        self.after(duration, lambda: self.notification_label.configure(text=""))
