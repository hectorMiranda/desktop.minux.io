import customtkinter as ctk
from PIL import Image

class TabView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tabs = {}  # {tab_id: {"title": str, "content": widget}}
        self.current_tab = None
        
        # Create tab bar
        self.tab_bar = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0, height=35)
        self.tab_bar.pack(fill="x", padx=0, pady=0)
        self.tab_bar.pack_propagate(False)
        
        # Create content area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content_area.pack(fill="both", expand=True)
        
        try:
            self.close_image = ctk.CTkImage(
                light_image=Image.open("media/icons/close.png"),
                dark_image=Image.open("media/icons/close.png"),
                size=(12, 12)
            )
        except Exception as e:
            print(f"Error loading tab icons: {e}")
            self.close_image = None
    
    def add_tab(self, title, content, select=True):
        # Create tab button frame
        tab_frame = ctk.CTkFrame(self.tab_bar, fg_color="transparent", corner_radius=0)
        tab_frame.pack(side="left", padx=(0, 1))
        
        # Create tab button
        tab_btn = ctk.CTkButton(
            tab_frame,
            text=title,
            fg_color="transparent",
            hover_color="gray20",
            corner_radius=0,
            height=35,
            compound="left",
            command=lambda: self.select_tab(title)
        )
        tab_btn.pack(side="left")
        
        # Create close button
        close_btn = ctk.CTkButton(
            tab_frame,
            text="",
            image=self.close_image,
            fg_color="transparent",
            hover_color="gray20",
            corner_radius=0,
            width=20,
            height=35,
            command=lambda: self.close_tab(title)
        )
        close_btn.pack(side="right")
        
        # Store tab info
        self.tabs[title] = {
            "frame": tab_frame,
            "button": tab_btn,
            "close": close_btn,
            "content": content
        }
        
        # Select the new tab if requested
        if select or len(self.tabs) == 1:
            self.select_tab(title)
    
    def select_tab(self, title):
        # Hide current tab content
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab]["content"].pack_forget()
            self.tabs[self.current_tab]["frame"].configure(fg_color="transparent")
            self.tabs[self.current_tab]["button"].configure(fg_color="transparent")
            self.tabs[self.current_tab]["close"].configure(fg_color="transparent")
        
        # Show new tab content
        if title in self.tabs:
            self.current_tab = title
            self.tabs[title]["content"].pack(in_=self.content_area, fill="both", expand=True)
            self.tabs[title]["frame"].configure(fg_color="gray20")
            self.tabs[title]["button"].configure(fg_color="gray20")
            self.tabs[title]["close"].configure(fg_color="gray20")
    
    def close_tab(self, title):
        if title in self.tabs:
            # Remove tab widgets
            self.tabs[title]["frame"].destroy()
            self.tabs[title]["content"].destroy()
            
            # If closing current tab, select another one
            if self.current_tab == title:
                remaining_tabs = list(self.tabs.keys())
                remaining_tabs.remove(title)
                if remaining_tabs:
                    self.select_tab(remaining_tabs[0])
                else:
                    self.current_tab = None
            
            # Remove tab from storage
            del self.tabs[title] 