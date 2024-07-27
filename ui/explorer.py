import os
import customtkinter as ctk
from PIL import Image

class FileExplorer(ctk.CTkFrame):
    def __init__(self, parent, on_file_select):
        super().__init__(parent)
        self.on_file_select = on_file_select
        
        # Create main frame
        self.explorer_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.explorer_frame.pack(fill="both", expand=True)
        
        # Create tree view for files
        self.tree = ctk.CTkScrollableFrame(self.explorer_frame, fg_color="transparent", corner_radius=0)
        self.tree.pack(fill="both", expand=True)
        
        # Load icons
        try:
            self.folder_image = ctk.CTkImage(
                light_image=Image.open("media/icons/folder.png"),
                dark_image=Image.open("media/icons/folder.png"),
                size=(16, 16)
            )
            self.file_image = ctk.CTkImage(
                light_image=Image.open("media/icons/file.png"),
                dark_image=Image.open("media/icons/file.png"),
                size=(16, 16)
            )
        except Exception as e:
            print(f"Error loading explorer icons: {e}")
            self.folder_image = None
            self.file_image = None
        
        self.refresh()
    
    def refresh(self, path="."):
        # Clear existing items
        for widget in self.tree.winfo_children():
            widget.destroy()
        
        # Get sorted list of directories and files
        try:
            items = os.listdir(path)
            dirs = sorted([x for x in items if os.path.isdir(os.path.join(path, x))])
            files = sorted([x for x in items if os.path.isfile(os.path.join(path, x))])
            
            # Add directories first
            for dir_name in dirs:
                if not dir_name.startswith('.'):  # Skip hidden directories
                    self.add_item(dir_name, is_dir=True)
            
            # Then add files
            for file_name in files:
                if not file_name.startswith('.'):  # Skip hidden files
                    self.add_item(file_name, is_dir=False)
                    
        except Exception as e:
            print(f"Error reading directory: {e}")
    
    def add_item(self, name, is_dir=False):
        frame = ctk.CTkFrame(self.tree, fg_color="transparent", corner_radius=0, height=25)
        frame.pack(fill="x", padx=0, pady=(0, 1))
        frame.pack_propagate(False)
        
        # Indent based on directory depth
        indent = 20 * name.count(os.sep)
        
        # Create button with icon and text
        btn = ctk.CTkButton(
            frame,
            image=self.folder_image if is_dir else self.file_image,
            text=os.path.basename(name),
            anchor="w",
            fg_color="transparent",
            hover_color="gray20",
            corner_radius=0,
            height=25,
            compound="left",
            command=lambda: self.item_clicked(name, is_dir)
        )
        btn.pack(fill="x", padx=(indent, 0))
    
    def item_clicked(self, name, is_dir):
        if is_dir:
            # Expand/collapse directory
            pass
        else:
            # Open file in new tab
            self.on_file_select(name) 