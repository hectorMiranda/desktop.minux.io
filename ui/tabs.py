import customtkinter as ctk
import tkinter as tk
from PIL import Image
import logging
import os
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)

class VSCodeTabView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure main frame
        self.configure(fg_color="#1e1e1e", corner_radius=0)
        
        # Configure scrollbar style for dark theme
        style = ttk.Style()
        style.configure(
            "Dark.Vertical.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            bordercolor="#1e1e1e",
            arrowcolor="#6b6b6b",
            lightcolor="#1e1e1e",
            darkcolor="#1e1e1e"
        )
        style.configure(
            "Dark.Horizontal.TScrollbar",
            background="#1e1e1e",
            troughcolor="#2d2d2d",
            bordercolor="#1e1e1e",
            arrowcolor="#6b6b6b",
            lightcolor="#1e1e1e",
            darkcolor="#1e1e1e"
        )
        
        # Initialize state
        self._tabs = {}  # {name: {"frame": frame, "button_container": container, "button": button, "close_button": button}}
        self._tab_dict = {}  # For compatibility with existing code
        self._tab_order = []  # List to maintain tab order
        self._current_tab = None
        self._last_active_tab = None
        
        # Create tab bar
        self._create_tab_bar()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Bind events
        self._bind_events()
        
    def _create_tab_bar(self):
        """Create the tab bar with VSCode styling"""
        # Tab bar container
        self.tab_bar = ctk.CTkFrame(self, fg_color="#252526", height=35, corner_radius=0)
        self.tab_bar.grid(row=0, column=0, sticky="ew")
        self.tab_bar.grid_propagate(False)
        
        # Container for tabs
        self.tab_container = ctk.CTkFrame(self.tab_bar, fg_color="transparent")
        self.tab_container.pack(side="left", fill="y")
        
        # Content area - ensure it fills the space
        self.content_area = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=0)
        self.content_area.grid(row=1, column=0, sticky="nsew")
        
        # Configure content area grid
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        
    def add(self, name: str) -> ctk.CTkFrame:
        """Add a new tab or focus existing one"""
        if name in self._tabs:
            self.set(name)
            return self._tabs[name]["frame"]
            
        # Create tab frame that fills the content area
        tab_frame = ctk.CTkFrame(self.content_area, fg_color="#1e1e1e", corner_radius=0)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        # Create tab button container with less width
        button_container = ctk.CTkFrame(self.tab_container, fg_color="transparent", height=35)
        button_container.pack(side="left")
        button_container.pack_propagate(False)
        
        # Create tab button with dynamic width
        tab_button = ctk.CTkButton(
            button_container,
            text=name,
            width=30,  # Small initial width, will expand based on text
            height=35,
            fg_color="#2d2d2d",
            hover_color="#2d2d2d",
            text_color="#969696",
            font=("Segoe UI", 11),
            corner_radius=0,
            command=lambda: self.set(name)
        )
        tab_button.pack(side="left", fill="y", padx=(5, 25))  # Add padding for close button
        
        # Create close button closer to text
        close_button = ctk.CTkButton(
            button_container,
            text="×",
            width=16,
            height=16,
            fg_color="transparent",
            hover_color="#404040",
            text_color="#969696",
            font=("Segoe UI", 13),
            corner_radius=0,
            command=lambda: self.delete(name)
        )
        
        # Calculate text width and position close button accordingly
        text_width = len(name) * 7  # Approximate width per character
        button_container.configure(width=text_width + 40)  # Text width + padding + close button
        close_button.place(x=text_width + 10, rely=0.5, anchor="w")  # Position right after text
        
        # Store tab info
        self._tabs[name] = {
            "frame": tab_frame,
            "button_container": button_container,
            "button": tab_button,
            "close_button": close_button,
            "modified": False
        }
        
        # Update compatibility dict
        self._tab_dict[name] = tab_frame
        
        # Update tab order
        self._tab_order.append(name)
        
        # Set as current if first tab
        if len(self._tabs) == 1:
            self.set(name)
        
        return tab_frame
        
    def delete(self, name: str) -> None:
        """Delete a tab and clean up"""
        if name not in self._tabs:
            return
            
        # Get tab info
        tab = self._tabs[name]
        
        # Clean up widgets
        tab["frame"].destroy()
        tab["button_container"].destroy()
        
        # Update state
        self._tab_order.remove(name)
        del self._tabs[name]
        del self._tab_dict[name]
        
        # Update current tab
        if name == self._current_tab:
            if self._last_active_tab and self._last_active_tab in self._tabs:
                self.set(self._last_active_tab)
            elif self._tab_order:
                self.set(self._tab_order[-1])
            else:
                self._current_tab = None
                self._last_active_tab = None
                
        self._update_tab_appearance()
        
    def set(self, name: str) -> None:
        """Set the active tab"""
        if name not in self._tabs or name == self._current_tab:
            return
            
        # Update last active tab
        if self._current_tab:
            self._last_active_tab = self._current_tab
            
        # Hide current content
        if self._current_tab and self._current_tab in self._tabs:
            self._tabs[self._current_tab]["frame"].grid_remove()
            
        # Show new content - ensure it fills the space
        self._tabs[name]["frame"].grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self._current_tab = name
        
        # Update appearance
        self._update_tab_appearance()
        
    def get(self) -> str:
        """Get current tab name"""
        return self._current_tab
        
    def tab(self, name: str) -> ctk.CTkFrame:
        """Get tab frame by name"""
        return self._tabs[name]["frame"] if name in self._tabs else None
        
    def set_modified(self, name: str, modified: bool = True):
        """Set tab modified state"""
        if name in self._tabs:
            self._tabs[name]["modified"] = modified
            self._update_tab_appearance()
            
    def _update_tab_appearance(self):
        """Update the appearance of all tabs"""
        for name, tab in self._tabs.items():
            is_current = name == self._current_tab
            
            # Update button appearance
            tab["button"].configure(
                fg_color="#1e1e1e" if is_current else "#2d2d2d",
                text_color="#ffffff" if is_current else "#969696",
                border_width=1,
                border_color="#007acc" if is_current else "#252526"
            )
            
            # Update close button color
            tab["close_button"].configure(
                text_color="#cccccc" if is_current else "#969696"
            )
            
            # Add modified indicator if needed
            text = name + " •" if tab["modified"] else name
            tab["button"].configure(text=text)
            
    def _bind_events(self):
        """Bind mouse and keyboard events"""
        # Tab bar scrolling
        self.tab_bar.bind("<MouseWheel>", self._on_mousewheel)
        self.tab_bar.bind("<Button-2>", self._on_tab_middle_click)  # Middle click to close
        
        # Window bindings for keyboard shortcuts
        self.master.bind("<Control-Tab>", self._next_tab)
        self.master.bind("<Control-Shift-Tab>", self._previous_tab)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling on tab bar"""
        self.tab_container.winfo_children()[0].pack_configure(
            padx=(max(0, self.tab_container.winfo_x() + event.delta), 0)
        )
        
    def _on_tab_middle_click(self, event):
        """Handle middle click to close tab"""
        for name, tab in self._tabs.items():
            if tab["button_container"].winfo_containing(event.x_root, event.y_root):
                self.delete(name)
                break
                
    def _next_tab(self, event=None):
        """Switch to next tab"""
        if not self._tab_order:
            return
            
        current_index = self._tab_order.index(self._current_tab)
        next_index = (current_index + 1) % len(self._tab_order)
        self.set(self._tab_order[next_index])
        
    def _previous_tab(self, event=None):
        """Switch to previous tab"""
        if not self._tab_order:
            return
            
        current_index = self._tab_order.index(self._current_tab)
        prev_index = (current_index - 1) % len(self._tab_order)
        self.set(self._tab_order[prev_index]) 