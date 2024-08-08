import os
import customtkinter as ctk
from PIL import Image
import tkinter as tk

class FileExplorer(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="#252526", corner_radius=0)
        self.app = app  # Store reference to main app
        
        # Create header
        self.header = ctk.CTkFrame(self, fg_color="#252526", height=35, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Add EXPLORER text
        self.title_label = ctk.CTkLabel(
            self.header,
            text="EXPLORER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#BBBBBB"
        )
        self.title_label.pack(side="left", padx=10)
        
        # Create toolbar
        self.toolbar = ctk.CTkFrame(self, fg_color="#252526", height=35, corner_radius=0)
        self.toolbar.pack(fill="x", side="top")
        self.toolbar.pack_propagate(False)
        
        # Add toolbar buttons with proper VSCode icons
        toolbar_buttons = [
            ("New File", "add.png", self.create_new_file),
            ("New Folder", "folder.png", self.create_new_folder),
            ("Refresh", "refresh.png", self.refresh_tree),
            ("Collapse", "collapse.png", self.collapse_all)
        ]
        
        for text, icon_name, command in toolbar_buttons:
            try:
                icon = ctk.CTkImage(
                    light_image=Image.open(f"media/icons/{icon_name}"),
                    dark_image=Image.open(f"media/icons/{icon_name}"),
                    size=(16, 16)
                )
                btn = ctk.CTkButton(
                    self.toolbar,
                    text="",
                    image=icon,
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color="#404040",
                    text_color="#858585",
                    command=command,
                    corner_radius=4
                )
                btn.pack(side="left", padx=2)
                if hasattr(self.app, 'create_tooltip'):
                    self.app.create_tooltip(btn, text)
            except Exception as e:
                print(f"Failed to load icon {icon_name}: {e}")
        
        # Create tree view container
        self.tree_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#424242",
            scrollbar_button_hover_color="#4F4F4F"
        )
        self.tree_container.pack(fill="both", expand=True)
        
        # Initialize empty tree
        self.current_path = None
        self.tree_items = {}
        self.selected_item = None
        self.refresh_tree()
        
    def create_tree_item(self, parent, name, path, is_dir, level):
        # Create frame for this item
        item_frame = ctk.CTkFrame(parent, fg_color="transparent", height=22)
        item_frame.pack(fill="x")
        item_frame.pack_propagate(False)
        
        # Add indentation
        if level > 0:
            indent = ctk.CTkFrame(item_frame, fg_color="transparent", width=level * 16)
            indent.pack(side="left")
        
        # Add expand/collapse arrow for directories
        if is_dir:
            arrow = "▶" if not self.tree_items.get(path, {}).get("expanded", False) else "▼"
            arrow_label = ctk.CTkLabel(
                item_frame,
                text=arrow,
                font=ctk.CTkFont(size=10),
                width=16,
                text_color="#858585"
            )
            arrow_label.pack(side="left")
            arrow_label.bind("<Button-1>", lambda e, p=path: self.toggle_directory(p))
        else:
            spacer = ctk.CTkFrame(item_frame, fg_color="transparent", width=16)
            spacer.pack(side="left")
        
        # Add icon
        try:
            icon_name = "folder.png" if is_dir else self.get_file_icon(name)
            icon = ctk.CTkImage(
                light_image=Image.open(f"media/icons/{icon_name}"),
                dark_image=Image.open(f"media/icons/{icon_name}"),
                size=(16, 16)
            )
            icon_label = ctk.CTkLabel(
                item_frame,
                text="",
                image=icon,
                width=20
            )
        except Exception as e:
            # Fallback to text icons
            icon = "📁" if is_dir else "📄"
            icon_label = ctk.CTkLabel(
                item_frame,
                text=icon,
                font=ctk.CTkFont(size=14),
                width=20,
                text_color="#858585"
            )
        icon_label.pack(side="left")
        
        # Add name label
        name_label = ctk.CTkLabel(
            item_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color="#CCCCCC"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Store item info
        self.tree_items[path] = {
            "frame": item_frame,
            "is_dir": is_dir,
            "level": level,
            "expanded": False,
            "children_container": None,
            "arrow_label": arrow_label if is_dir else None
        }
        
        # Bind click events
        for widget in [item_frame, name_label, icon_label]:
            widget.bind("<Button-1>", lambda e, p=path, d=is_dir: self.item_clicked(p, d))
            widget.bind("<Double-Button-1>", lambda e, p=path, d=is_dir: self.item_double_clicked(p, d))
        
        # Change color on hover and selection
        def on_enter(e):
            if self.selected_item != path:
                item_frame.configure(fg_color="#2A2D2E")
            
        def on_leave(e):
            if self.selected_item != path:
                item_frame.configure(fg_color="transparent")
        
        for widget in [item_frame, name_label, icon_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
    def get_file_icon(self, filename):
        """Get the appropriate icon for a file based on its extension"""
        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.py': 'python.png',
            '.js': 'javascript.png',
            '.html': 'html.png',
            '.css': 'css.png',
            '.json': 'json.png',
            '.md': 'markdown.png',
            '.txt': 'text.png',
            '.gitignore': 'git.png',
            'README.md': 'readme.png'
        }
        return icon_map.get(ext, 'file.png')
        
    def toggle_directory(self, path):
        """Toggle directory expansion/collapse"""
        item = self.tree_items.get(path)
        if item and item["is_dir"]:
            if item["expanded"]:
                # Update arrow
                if item["arrow_label"]:
                    item["arrow_label"].configure(text="▶")
                # Collapse
                if item["children_container"]:
                    item["children_container"].destroy()
                    item["children_container"] = None
                item["expanded"] = False
            else:
                # Update arrow
                if item["arrow_label"]:
                    item["arrow_label"].configure(text="▼")
                # Expand
                self.expand_directory(path, item)
                
    def expand_directory(self, path, item):
        """Expand a directory and show its contents"""
        if not item["is_dir"]:
            return
            
        # Create container for children
        container = ctk.CTkFrame(item["frame"].master, fg_color="transparent")
        container.pack(fill="x")
        item["children_container"] = container
        item["expanded"] = True
        
        try:
            # List directory contents
            entries = os.listdir(path)
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for entry in entries:
                if not entry.startswith('.'):  # Skip hidden files
                    entry_path = os.path.join(path, entry)
                    is_dir = os.path.isdir(entry_path)
                    self.create_tree_item(container, entry, entry_path, is_dir, item["level"] + 1)
        except Exception as e:
            print(f"Error expanding directory: {e}")
            
    def item_clicked(self, path, is_dir):
        """Handle item click"""
        # Update selection
        if self.selected_item:
            old_item = self.tree_items.get(self.selected_item)
            if old_item:
                old_item["frame"].configure(fg_color="transparent")
                
        self.selected_item = path
        self.tree_items[path]["frame"].configure(fg_color="#37373D")
        
        if not is_dir:
            # Open file in editor
            if hasattr(self.app, 'open_file'):
                self.app.open_file(path)
                
    def item_double_clicked(self, path, is_dir):
        """Handle item double click"""
        if is_dir:
            self.toggle_directory(path)
            
    def create_new_file(self):
        """Create a new file"""
        if self.selected_item and os.path.isdir(self.selected_item):
            parent_dir = self.selected_item
        else:
            parent_dir = self.current_path
            
        if parent_dir:
            # TODO: Implement new file dialog
            pass
            
    def create_new_folder(self):
        """Create a new folder"""
        if self.selected_item and os.path.isdir(self.selected_item):
            parent_dir = self.selected_item
        else:
            parent_dir = self.current_path
            
        if parent_dir:
            # TODO: Implement new folder dialog
            pass
            
    def collapse_all(self):
        """Collapse all expanded directories"""
        for path, item in self.tree_items.items():
            if item["is_dir"] and item["expanded"]:
                self.toggle_directory(path)
                
    def refresh_tree(self):
        """Refresh the file tree"""
        # Clear existing tree items
        for widget in self.tree_container.winfo_children():
            widget.destroy()
        self.tree_items.clear()
        self.selected_item = None
        
        # Get current working directory
        if self.current_path is None:
            self.current_path = os.getcwd()
            
        # Create root item
        root_name = os.path.basename(self.current_path) or self.current_path
        self.create_tree_item(self.tree_container, root_name, self.current_path, True, 0)
        
        # Expand root
        self.toggle_directory(self.current_path) 