import customtkinter as ctk
import tkinter as tk
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class TabView(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set the background color for the main frame
        self.configure(fg_color="#1e1e1e")
        
        # Create tab bar (fixed height of 35)
        self.tab_bar = ctk.CTkFrame(self, height=35, fg_color="#1e1e1e")
        self.tab_bar.pack(side="top", fill="x", pady=0)
        self.tab_bar.pack_propagate(False)
        
        # Create tab container for buttons
        self.tab_container = ctk.CTkFrame(self.tab_bar, fg_color="transparent")
        self.tab_container.pack(side="left", fill="y")
        
        # Initialize tab tracking
        self.tabs = {}
        self.current_tab = None
        
    def add_tab(self, title, content):
        """Add a new tab with the given title and content"""
        try:
            # Create tab button frame
            tab_frame = ctk.CTkFrame(self.tab_container, fg_color="transparent")
            tab_frame.pack(side="left", padx=1)
            
            # Create tab button
            tab_button = ctk.CTkButton(
                tab_frame,
                text=title,
                width=120,
                height=35,
                fg_color="#252526",
                hover_color="#404040",
                corner_radius=0,
                command=lambda: self.select_tab(title)
            )
            tab_button.pack(side="left")
            
            # Create close button
            close_button = ctk.CTkButton(
                tab_frame,
                text="×",
                width=20,
                height=35,
                fg_color="#252526",
                hover_color="#404040",
                corner_radius=0,
                command=lambda: self.close_tab(title)
            )
            close_button.pack(side="left")
            
            # Configure content
            if isinstance(content, (ctk.CTkBaseClass, tk.Widget)):
                content.pack_forget()  # Ensure it's not visible initially
                content.master = self  # Set parent to main frame
            
            # Store tab information
            self.tabs[title] = {
                "button_frame": tab_frame,
                "button": tab_button,
                "content": content
            }
            
            # Select the new tab
            self.select_tab(title)
            
        except Exception as e:
            logger.error(f"Error adding tab: {str(e)}")
            raise

    def select_tab(self, title):
        """Select the specified tab"""
        if title not in self.tabs or title == self.current_tab:
            return
            
        # Update button appearances
        for tab_title, tab_info in self.tabs.items():
            tab_info["button"].configure(fg_color="#252526")
            
        self.tabs[title]["button"].configure(fg_color="#1e1e1e")
        
        # Hide all content
        for tab_info in self.tabs.values():
            content = tab_info["content"]
            if isinstance(content, (ctk.CTkBaseClass, tk.Widget)):
                content.pack_forget()
        
        # Show selected content
        content = self.tabs[title]["content"]
        if isinstance(content, (ctk.CTkBaseClass, tk.Widget)):
            content.pack(side="top", fill="both", expand=True, pady=0)
        
        self.current_tab = title

    def close_tab(self, title):
        """Close the specified tab"""
        if title not in self.tabs:
            return
            
        # Get remaining tabs
        remaining_tabs = [t for t in self.tabs.keys() if t != title]
        
        # Clean up the tab
        if title == self.current_tab:
            content = self.tabs[title]["content"]
            if isinstance(content, (ctk.CTkBaseClass, tk.Widget)):
                content.pack_forget()
        
        self.tabs[title]["button_frame"].destroy()
        del self.tabs[title]
        
        # Select another tab if available
        if remaining_tabs:
            self.select_tab(remaining_tabs[0])
        else:
            self.current_tab = None

    def get_current_tab(self):
        """Get the currently selected tab"""
        return self.current_tab 