import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=22, fg_color="#007acc", corner_radius=0)
        
        # Create left, middle, and right sections
        self.left_frame = ctk.CTkFrame(self, fg_color="#007acc", corner_radius=0, height=22)
        self.left_frame.grid(row=0, column=0, sticky="w")
        self.left_frame.grid_propagate(False)
        
        self.middle_frame = ctk.CTkFrame(self, fg_color="#007acc", corner_radius=0, height=22)
        self.middle_frame.grid(row=0, column=1, sticky="ew")
        self.middle_frame.grid_propagate(False)
        
        self.right_frame = ctk.CTkFrame(self, fg_color="#007acc", corner_radius=0, height=22)
        self.right_frame.grid(row=0, column=2, sticky="e")
        self.right_frame.grid_propagate(False)
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)  # Middle section expands
        self.grid_columnconfigure((0, 2), weight=0)  # Left and right sections fixed
        
        # Initialize default items
        self._create_default_items()
        
    def _create_default_items(self):
        """Create default status bar items"""
        # Left section items
        self.branch_item = self._create_clickable_item(self.left_frame, "main", "⎇", command=self._branch_click)
        self.sync_item = self._create_clickable_item(self.left_frame, "↻ 0 ↑0 ↓0", command=self._sync_click)
        self.error_item = self._create_status_item(self.left_frame, "✓ 0  ⚠ 0")
        
        # Right section items (in reverse order as they're packed from right)
        self.encoding_item = self._create_clickable_item(self.right_frame, "UTF-8", command=self._encoding_click)
        self.line_ending_item = self._create_clickable_item(self.right_frame, "LF", command=self._line_ending_click)
        self.cursor_pos_item = self._create_status_item(self.right_frame, "Ln 1, Col 1")
        
    def _create_status_item(self, parent, text, icon=None):
        """Create a non-clickable status item"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=22)
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        
        if icon:
            icon_label = ctk.CTkLabel(
                frame,
                text=icon,
                font=("Segoe UI", 11, "normal"),  # VSCode's font weight
                text_color="#ffffff",
                width=16
            )
            icon_label.pack(side="left", padx=(4, 0))  # VSCode's exact padding
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Segoe UI", 11, "normal"),  # VSCode's font weight
            text_color="#ffffff"
        )
        label.pack(side="left", padx=4)  # VSCode's exact padding
        
        return frame
        
    def _create_clickable_item(self, parent, text, icon=None, command=None):
        """Create a clickable status item"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=22)
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        
        button = ctk.CTkButton(
            frame,
            text=icon + " " + text if icon else text,
            font=("Segoe UI", 11, "normal"),  # VSCode's font weight
            text_color="#ffffff",
            fg_color="transparent",
            hover_color="#1f8ad2",  # VSCode's exact hover color
            corner_radius=0,
            height=22,
            command=command
        )
        button.pack(side="left", fill="y", padx=0)
        
        # Add separator after clickable items
        separator = ctk.CTkFrame(parent, fg_color="#ffffff", width=1, height=14)
        separator.pack(side="left", padx=8)  # VSCode's exact separator spacing
        
        return frame
        
    def set_cursor_position(self, text):
        """Update cursor position display"""
        if hasattr(self, 'cursor_pos_item'):
            for widget in self.cursor_pos_item.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text=text)
                    
    def _branch_click(self):
        """Handle branch item click"""
        pass
        
    def _sync_click(self):
        """Handle sync item click"""
        pass
        
    def _encoding_click(self):
        """Handle encoding item click"""
        pass
        
    def _line_ending_click(self):
        """Handle line ending item click"""
        pass
        
    def update_cursor_position(self, line, column):
        """Update the cursor position display"""
        self.cursor_pos_item.winfo_children()[0].configure(text=f"Ln {line}, Col {column}")
        
    def update_file_type(self, file_type):
        """Update the file type display"""
        self.encoding_item.winfo_children()[0].configure(text=file_type)
        
    def update_encoding(self, encoding):
        """Update the encoding display"""
        self.encoding_item.winfo_children()[0].configure(text=encoding)
        
    def update_line_ending(self, line_ending):
        """Update the line ending display"""
        self.line_ending_item.winfo_children()[0].configure(text=line_ending)
        
    def set_warning_count(self, count):
        """Update the warning count"""
        self.sync_item.winfo_children()[0].configure(text=f"⚡ {count}")
        
    def set_error_count(self, count):
        """Update the error count"""
        self.error_item.winfo_children()[0].configure(text=f"⚠ {count}")
        
    def show_notification(self, message, duration=3000):
        """Show a temporary notification in the status bar"""
        self.notification_label.configure(text=message)
        self.after(duration, lambda: self.notification_label.configure(text=""))
