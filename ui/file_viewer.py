import customtkinter as ctk

class FileViewer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create text widget for file content
        self.text = ctk.CTkTextbox(
            self,
            fg_color="transparent",
            corner_radius=0,
            wrap="none",
            font=("Cascadia Code", 12)  # Using a monospace font like VSCode
        )
        self.text.pack(fill="both", expand=True)
        
        # Add horizontal scrollbar
        self.h_scroll = ctk.CTkScrollbar(
            self,
            orientation="horizontal",
            command=self.text.xview
        )
        self.h_scroll.pack(fill="x", side="bottom")
        
        # Configure text widget to use scrollbars
        self.text.configure(xscrollcommand=self.h_scroll.set)
        
        # Make text widget read-only
        self.text.configure(state="disabled")
    
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.text.configure(state="disabled")
        except Exception as e:
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", f"Error loading file: {e}")
            self.text.configure(state="disabled") 