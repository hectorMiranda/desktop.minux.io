import tkinter as tk
from tkinter import messagebox, Menu
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def show_welcome():
    clear_frame()
    welcome_label = tk.Label(main_frame, text="Welcome to the Control Center", font=("Arial", 24))
    welcome_label.pack(pady=20)

def open_todo_app():
    clear_frame()
    create_todo_app()

def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

def create_todo_app():
    task_var = tk.StringVar(main_frame)
    task_entry = tk.Entry(main_frame, textvariable=task_var, width=45)
    task_entry.pack(pady=10)

    listbox_tasks = tk.Listbox(main_frame, width=50, height=10)
    listbox_tasks.pack(pady=10)

    # Load existing tasks from Firestore
    def load_tasks():
        docs = db.collection('todos').stream()
        for doc in docs:
            task = doc.to_dict()
            listbox_tasks.insert(tk.END, task['task'])

    def add_task():
        task = task_var.get()
        if task != "":
            # Add to Firestore
            doc_ref = db.collection('todos').add({'task': task, 'done': False})
            task_entry.delete(0, tk.END)
            listbox_tasks.insert(tk.END, task)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    add_task_btn = tk.Button(main_frame, text="Add Task", width=42, command=add_task)
    add_task_btn.pack(pady=10)

    # Additional functionalities like mark_done and delete_task need Firestore document IDs
    # These functionalities would require storing and using document IDs from Firestore
    # This basic example does not include these for simplicity

    load_tasks()  # Call to load tasks from Firestore

root = tk.Tk()
root.title("Control Center")

# Make the window not full-screen by default for demonstration
root.attributes('-fullscreen', False)

# Allow exiting full-screen mode with Escape key
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

# Create a menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)

# Add menu items
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Welcome", command=show_welcome)
file_menu.add_command(label="Open To-Do App", command=open_todo_app)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Initially show welcome message
show_welcome()

# Run the application
root.mainloop()
