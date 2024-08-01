import os
import customtkinter as ctk
from PIL import Image

class FileExplorer(ctk.CTkFrame):
    def __init__(self, parent, on_file_select):
        super().__init__(parent)
        self.on_file_select = on_file_select
        self.expanded_paths = set()  # Track expanded folders
        
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
            # Try to load folder-open icon, fall back to folder icon if not available
            try:
                folder_open = Image.open("media/icons/folder-open.png")
            except:
                folder_open = Image.open("media/icons/folder.png")
            self.folder_open_image = ctk.CTkImage(
                light_image=folder_open,
                dark_image=folder_open,
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
            self.folder_open_image = None
            self.file_image = None
        
        self.refresh()
    
    def refresh(self, base_path="."):
        # Clear existing items
        for widget in self.tree.winfo_children():
            widget.destroy()
        
        # Walk through directory tree
        self._add_directory_contents(base_path, level=0)
    
    def _add_directory_contents(self, path, level=0):
        try:
            # Get sorted list of directories and files
            items = os.listdir(path)
            dirs = sorted([x for x in items if os.path.isdir(os.path.join(path, x))])
            files = sorted([x for x in items if os.path.isfile(os.path.join(path, x))])
            
            # Add directories first
            for dir_name in dirs:
                if not dir_name.startswith('.'):  # Skip hidden directories
                    full_path = os.path.join(path, dir_name)
                    self.add_item(full_path, is_dir=True, level=level)
                    # If directory is expanded, show its contents
                    if full_path in self.expanded_paths:
                        self._add_directory_contents(full_path, level + 1)
            
            # Then add files
            for file_name in files:
                if not file_name.startswith('.'):  # Skip hidden files
                    full_path = os.path.join(path, file_name)
                    self.add_item(full_path, is_dir=False, level=level)
                    
        except Exception as e:
            print(f"Error reading directory {path}: {e}")
    
    def add_item(self, path, is_dir=False, level=0):
        # Create main frame for the entire row
        frame = ctk.CTkFrame(self.tree, fg_color="transparent", corner_radius=0, height=25)
        frame.pack(fill="x", padx=0, pady=(0, 1))
        frame.pack_propagate(False)
        
        # Calculate indent based on level
        indent = 20 * level
        
        # Create button with icon and text
        is_expanded = path in self.expanded_paths
        
        # Add expansion indicator for directories
        if is_dir:
            expander_frame = ctk.CTkFrame(frame, fg_color="transparent", width=20, height=25)
            expander_frame.pack(side="left", padx=(indent, 0))
            expander_frame.pack_propagate(False)
            
            expander = ctk.CTkLabel(
                expander_frame,
                text="▼" if is_expanded else "▶",
                width=20,
                anchor="w",
                text_color="gray70"
            )
            expander.pack(expand=True)
            
            # Make expander clickable
            expander.bind("<Button-1>", lambda e, p=path: self.item_clicked(p, True))
            # Change cursor on hover
            expander.bind("<Enter>", lambda e: expander.configure(cursor="hand2"))
            expander.bind("<Leave>", lambda e: expander.configure(cursor=""))
            
            indent = 0  # Reset indent since we've already applied it
        
        # Select appropriate icon
        icon = self.folder_open_image if (is_dir and is_expanded) else (self.folder_image if is_dir else self.file_image)
        
        # Create button for the item
        btn = ctk.CTkButton(
            frame,
            image=icon,
            text=os.path.basename(path),
            anchor="w",
            fg_color="transparent",
            hover_color="gray20",
            corner_radius=0,
            height=25,
            compound="left",
            command=lambda p=path, d=is_dir: self.item_clicked(p, d)
        )
        btn.pack(fill="x", padx=(indent, 0))
        
        # Make the entire row interactive for directories
        if is_dir:
            frame.bind("<Enter>", lambda e: btn.configure(fg_color="gray20"))
            frame.bind("<Leave>", lambda e: btn.configure(fg_color="transparent"))
            frame.bind("<Button-1>", lambda e, p=path: self.item_clicked(p, True))
    
    def item_clicked(self, path, is_dir):
        if is_dir:
            if path in self.expanded_paths:
                self.expanded_paths.remove(path)
            else:
                self.expanded_paths.add(path)
            self.refresh()  # Refresh to show/hide contents
        else:
            # Open file in new tab
            self.on_file_select(path) 