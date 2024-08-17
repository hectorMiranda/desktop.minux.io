import os
import customtkinter as ctk
from PIL import Image, ImageTk
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
        item_frame.pack(fill="x", padx=0, pady=0)
        item_frame.pack_propagate(False)
        
        # Add indentation
        if level > 0:
            indent = ctk.CTkFrame(item_frame, fg_color="transparent", width=level * 16)
            indent.pack(side="left", padx=0, pady=0)
        
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
            arrow_label.pack(side="left", padx=0, pady=0)
            
            # Bind arrow events
            def on_arrow_click(e):
                self.toggle_directory(path)
                return "break"  # Prevent event propagation
                
            def on_arrow_enter(e):
                arrow_label.configure(text_color="#CCCCCC")
                
            def on_arrow_leave(e):
                arrow_label.configure(text_color="#858585")
                
            arrow_label.bind("<Button-1>", on_arrow_click)
            arrow_label.bind("<Enter>", on_arrow_enter)
            arrow_label.bind("<Leave>", on_arrow_leave)
        else:
            spacer = ctk.CTkFrame(item_frame, fg_color="transparent", width=16)
            spacer.pack(side="left", padx=0, pady=0)
        
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
            if is_dir:
                icon = "📁"
            elif self.is_image_file(name):
                icon = "🖼"
            elif self.is_text_file(name):
                icon = "📄"
            else:
                icon = "📦"
            icon_label = ctk.CTkLabel(
                item_frame,
                text=icon,
                font=ctk.CTkFont(size=14),
                width=20,
                text_color="#858585"
            )
        icon_label.pack(side="left", padx=(2, 4), pady=0)
        
        # Add name label
        name_label = ctk.CTkLabel(
            item_frame,
            text=name,
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color="#CCCCCC"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=0, pady=0)
        
        # Store item info
        self.tree_items[path] = {
            "frame": item_frame,
            "is_dir": is_dir,
            "level": level,
            "expanded": False,
            "children_container": None,
            "arrow_label": arrow_label if is_dir else None,
            "name_label": name_label,
            "icon_label": icon_label
        }
        
        # Define event handlers
        def on_click(e):
            self.item_clicked(path, is_dir)
            return "break"  # Prevent event propagation
            
        def on_double_click(e):
            if is_dir:
                self.toggle_directory(path)
            else:
                self.item_clicked(path, is_dir)
            return "break"  # Prevent event propagation
            
        def on_enter(e):
            if self.selected_item != path:
                item_frame.configure(fg_color="#2A2D2E")
            
        def on_leave(e):
            if self.selected_item != path:
                item_frame.configure(fg_color="transparent")
        
        # Bind events to all components
        for widget in [item_frame, name_label, icon_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
    def get_file_icon(self, filename):
        """Get the appropriate icon for a file based on its extension"""
        ext = os.path.splitext(filename)[1].lower()
        name = os.path.basename(filename).lower()
        
        # Special files
        if name == 'dockerfile':
            return 'docker.svg'
        elif name == '.gitignore':
            return 'git.png'
        elif name == 'package.json':
            return 'npm.png'
        elif name == 'readme.md':
            return 'markdown.png'
        
        # Try extension without the dot for both .png and .svg
        if ext:
            ext_name = ext[1:]  # Remove the dot
            # Try PNG version
            if os.path.exists(os.path.join("media", "icons", f"{ext_name}.png")):
                return f"{ext_name}.png"
            # Try SVG version
            if os.path.exists(os.path.join("media", "icons", f"{ext_name}.svg")):
                return f"{ext_name}.svg"
        
        # Handle specific file types
        if self.is_image_file(filename):
            return 'image.png'
        elif ext in {'.exe', '.dll', '.so', '.dylib', '.bin', '.dat'}:
            return 'binary.png'
        elif ext in {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.c', '.h'}:
            return 'file.png'
        
        # Default to file icon
        return 'file.png'

    def is_image_file(self, filename):
        """Check if the file is an image"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp'}
        ext = os.path.splitext(filename)[1].lower()
        return ext in image_extensions

    def is_text_file(self, filename):
        """Check if the file is a text/code file"""
        text_extensions = {
            '.py', '.js', '.html', '.css', '.cpp', '.c', '.h', '.java',
            '.php', '.rb', '.go', '.ts', '.jsx', '.tsx', '.md', '.txt',
            '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf',
            '.config', '.rtf'
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in text_extensions
        
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
            
        # Create container for children that comes after the current item
        container = ctk.CTkFrame(self.tree_container, fg_color="transparent")
        container.pack(fill="x", after=item["frame"])
        item["children_container"] = container
        item["expanded"] = True
        
        try:
            # List directory contents
            entries = os.listdir(path)
            # Sort directories first, then files, both in alphabetical order
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for entry in entries:
                if not entry.startswith('.'):  # Skip hidden files
                    entry_path = os.path.join(path, entry)
                    is_dir = os.path.isdir(entry_path)
                    self.create_tree_item(container, entry, entry_path, is_dir, item["level"] + 1)
        except Exception as e:
            print(f"Error expanding directory: {e}")
            if item["arrow_label"]:
                item["arrow_label"].configure(text="▶")  # Reset arrow if failed
            if item["children_container"]:
                item["children_container"].destroy()
                item["children_container"] = None
            item["expanded"] = False
            
    def item_clicked(self, path, is_dir):
        """Handle item click"""
        # Update selection
        if self.selected_item:
            old_item = self.tree_items.get(self.selected_item)
            if old_item and old_item["frame"].winfo_exists():
                try:
                    old_item["frame"].configure(fg_color="transparent")
                except tk.TclError:
                    # Remove invalid item from tree_items
                    del self.tree_items[self.selected_item]
                
        # Clean up any destroyed items from tree_items
        invalid_paths = []
        for item_path, item_data in self.tree_items.items():
            if not item_data["frame"].winfo_exists():
                invalid_paths.append(item_path)
        for invalid_path in invalid_paths:
            del self.tree_items[invalid_path]
                
        self.selected_item = path
        current_item = self.tree_items.get(path)
        if current_item and current_item["frame"].winfo_exists():
            current_item["frame"].configure(fg_color="#37373D")
            
            if not is_dir:
                if self.is_image_file(path):
                    # Show image preview for image files
                    self.show_image_preview(path)
                else:
                    # Open file in editor for text files
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

    def show_image_preview(self, path):
        """Show image preview in a new tab"""
        try:
            # Get the file name for the tab title
            file_name = os.path.basename(path)
            
            # Create new tab using the app's tab view
            if hasattr(self.app, 'tab_view'):
                # Create tab
                tab = self.app.tab_view.add(file_name)
                
                # Create scrollable frame in the tab
                scroll_frame = ctk.CTkScrollableFrame(
                    tab,
                    fg_color="#1e1e1e",
                    corner_radius=0
                )
                scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
                
                # Load and display image
                image = Image.open(path)
                
                # Calculate new size while maintaining aspect ratio
                # Use tab size instead of fixed size
                tab.update_idletasks()  # Ensure we have correct dimensions
                max_width = tab.winfo_width() - 40  # Account for padding and scrollbar
                max_height = tab.winfo_height() - 40
                ratio = min(max_width/image.width, max_height/image.height)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                
                # Resize image if needed
                if ratio < 1:
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Create container for image and info
                content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                content_frame.pack(fill="both", expand=True)
                
                # Create and pack image label
                image_label = ctk.CTkLabel(
                    content_frame,
                    text="",
                    image=photo
                )
                image_label.image = photo  # Keep a reference to prevent garbage collection
                image_label.pack(padx=5, pady=5)
                
                # Add image info with monospace font
                info_text = (
                    f"Image: {file_name}\n"
                    f"Format: {image.format}\n"
                    f"Size: {image.width}x{image.height} pixels\n"
                    f"Mode: {image.mode}"
                )
                info_label = ctk.CTkLabel(
                    content_frame,
                    text=info_text,
                    font=("Cascadia Code", 11),
                    text_color="#CCCCCC",
                    justify="left"
                )
                info_label.pack(pady=5, anchor="w", padx=5)
                
                # Switch to the new tab
                self.app.tab_view.set(file_name)
                
                # Store reference to prevent garbage collection
                tab._image_preview = {
                    'photo': photo,
                    'image_label': image_label,
                    'info_label': info_label
                }
                
        except Exception as e:
            print(f"Error showing image preview: {e}")
            if hasattr(self.app, 'show_error_notification'):
                self.app.show_error_notification(f"Error showing image preview: {e}") 