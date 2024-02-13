import tkinter as tk
from tkinter import ttk, messagebox, Menu
import datetime
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
    entry_frame = tk.Frame(main_frame)
    entry_frame.pack(pady=10)

    task_var = tk.StringVar(entry_frame)
    task_entry = tk.Entry(entry_frame, textvariable=task_var, width=38)
    task_entry.pack(side="left")

    def add_task():
        task = task_var.get()
        if task != "":
            doc_ref = db.collection('todos').document()
            doc_ref.set({'task': task, 'done': False, 'completed_date': ''})
            load_tasks()
            task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    add_task_btn = tk.Button(entry_frame, text="Add Task", command=add_task)
    add_task_btn.pack(side="left", padx=5)

    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(expand=True, fill="both", pady=10)

    columns = ("task", "done", "completed_date")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.heading("task", text="Task")
    tree.heading("done", text="Done")
    tree.heading("completed_date", text="Completed Date")
    tree.column("done", width=50, anchor="center")
    tree.column("completed_date", width=100, anchor="center")

    vscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vscroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vscroll.set)
    tree.pack(expand=True, fill="both")

    # Context menu for deleting tasks
    context_menu = tk.Menu(tree, tearoff=0)
    context_menu.add_command(label="Delete Task", command=lambda: delete_task())

    def popup(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    tree.bind("<Button-3>", popup)  # Adjust "<Button-3>" as needed for macOS or other systems

    def delete_task():
        selected_item = tree.selection()
        if selected_item:
            item_id = selected_item[0]
            response = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
            if response:
                db.collection('todos').document(item_id).delete()
                tree.delete(item_id)
                load_tasks()

    def load_tasks():
        for i in tree.get_children():
            tree.delete(i)
        docs = db.collection('todos').stream()
        for doc in docs:
            task = doc.to_dict()['task']
            done = 'Yes' if doc.to_dict().get('done') else 'No'
            completed_date = doc.to_dict().get('completed_date', '')
            tree.insert("", tk.END, values=(task, done, completed_date), iid=doc.id)

    load_tasks()

root = tk.Tk()
root.title("Control Center")
root.attributes('-fullscreen', False)
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

menu_bar = Menu(root)
root.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Welcome", command=show_welcome)
file_menu.add_command(label="Open To-Do App", command=open_todo_app)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

show_welcome()

root.mainloop()
