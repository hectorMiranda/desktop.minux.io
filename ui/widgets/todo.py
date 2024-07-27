import customtkinter as ctk
from PIL import Image

class TodoWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create main frame
        self.todo_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.todo_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header
        self.header = ctk.CTkFrame(self.todo_frame, fg_color="transparent", corner_radius=0)
        self.header.pack(fill="x", pady=(0, 10))
        
        # Add task entry
        self.task_entry = ctk.CTkEntry(
            self.header,
            placeholder_text="Add a task...",
            height=35,
            corner_radius=0
        )
        self.task_entry.pack(side="left", fill="x", expand=True)
        
        # Add task button
        try:
            self.add_image = ctk.CTkImage(
                light_image=Image.open("media/icons/add.png"),
                dark_image=Image.open("media/icons/add.png"),
                size=(16, 16)
            )
            add_btn = ctk.CTkButton(
                self.header,
                text="",
                image=self.add_image,
                width=35,
                height=35,
                corner_radius=0,
                command=self.add_task
            )
        except Exception as e:
            print(f"Error loading add icon: {e}")
            add_btn = ctk.CTkButton(
                self.header,
                text="+",
                width=35,
                height=35,
                corner_radius=0,
                command=self.add_task
            )
        add_btn.pack(side="left", padx=(5, 0))
        
        # Create tasks list
        self.tasks_frame = ctk.CTkScrollableFrame(
            self.todo_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.tasks_frame.pack(fill="both", expand=True)
        
        # Initialize empty tasks list
        self.tasks = []
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            # Create task frame
            task_frame = ctk.CTkFrame(
                self.tasks_frame,
                fg_color="transparent",
                corner_radius=0,
                height=35
            )
            task_frame.pack(fill="x", pady=(0, 2))
            task_frame.pack_propagate(False)
            
            # Add checkbox
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                task_frame,
                text=task_text,
                variable=var,
                corner_radius=0,
                command=lambda: self.toggle_task(checkbox, task_frame)
            )
            checkbox.pack(side="left", padx=5)
            
            # Add delete button
            try:
                self.delete_image = ctk.CTkImage(
                    light_image=Image.open("media/icons/close.png"),
                    dark_image=Image.open("media/icons/close.png"),
                    size=(12, 12)
                )
                delete_btn = ctk.CTkButton(
                    task_frame,
                    text="",
                    image=self.delete_image,
                    width=20,
                    height=20,
                    corner_radius=0,
                    command=lambda: self.delete_task(task_frame)
                )
            except Exception as e:
                print(f"Error loading delete icon: {e}")
                delete_btn = ctk.CTkButton(
                    task_frame,
                    text="×",
                    width=20,
                    height=20,
                    corner_radius=0,
                    command=lambda: self.delete_task(task_frame)
                )
            delete_btn.pack(side="right", padx=5)
            
            # Add task to list
            self.tasks.append({
                "frame": task_frame,
                "checkbox": checkbox,
                "delete": delete_btn,
                "completed": var
            })
            
            # Clear entry
            self.task_entry.delete(0, "end")
    
    def toggle_task(self, checkbox, task_frame):
        # Update task appearance based on completion
        if checkbox.get():
            checkbox.configure(text_color="gray50")
            task_frame.configure(fg_color="gray20")
        else:
            checkbox.configure(text_color="white")
            task_frame.configure(fg_color="transparent")
    
    def delete_task(self, task_frame):
        # Remove task from list and destroy widgets
        for task in self.tasks:
            if task["frame"] == task_frame:
                self.tasks.remove(task)
                task_frame.destroy()
                break 