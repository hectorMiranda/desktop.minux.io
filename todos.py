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
    task_var = tk.StringVar(main_frame)
    task_entry = tk.Entry(main_frame, textvariable=task_var, width=45)
    task_entry.pack(pady=10)

    columns = ("task", "done", "completed_date")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings")
    tree.heading("task", text="Task")
    tree.heading("done", text="Done")
    tree.heading("completed_date", text="Completed Date")
    tree.column("done", width=50, anchor="center")
    tree.column("completed_date", width=100, anchor="center")
    tree.pack(expand=True, fill="both", pady=10)

    def load_tasks():
        docs = db.collection('todos').stream()
        for doc in docs:
            task = doc.to_dict()['task']
            done = 'Yes' if doc.to_dict().get('done') else 'No'
            completed_date = doc.to_dict().get('completed_date', '')
            tree.insert("", tk.END, values=(task, done, completed_date), iid=doc.id)

    def add_task():
        task = task_var.get()
        if task != "":
            doc_ref = db.collection('todos').document()
            doc_ref.set({'task': task, 'done': False, 'completed_date': ''})
            tree.insert("", tk.END, values=(task, 'No', ''), iid=doc_ref.id)
            task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def toggle_done(event):
        region = tree.identify("region", event.x, event.y)
        column = tree.identify_column(event.x)
        if region == "cell" and column == "#2":  # Check if click is in the "Done" column
            item_id = tree.identify_row(event.y)
            item = tree.item(item_id)
            done_status = not (item['values'][1] == 'Yes')
            completed_date = str(datetime.date.today()) if done_status else ''
            db.collection('todos').document(item_id).update({'done': done_status, 'completed_date': completed_date})
            tree.item(item_id, values=(item['values'][0], 'Yes' if done_status else 'No', completed_date))

    def delete_task():
        selected_items = tree.selection()
        for item_id in selected_items:
            db.collection('todos').document(item_id).delete()
            tree.delete(item_id)

    add_task_btn = tk.Button(main_frame, text="Add Task", width=42, command=add_task)
    add_task_btn.pack(pady=10)

    delete_task_btn = tk.Button(main_frame, text="Delete Task", width=42, command=delete_task)
    delete_task_btn.pack(pady=5)

    # Bind the toggle_done function to mouse click events on the tree
    tree.bind("<Button-1>", toggle_done)

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
