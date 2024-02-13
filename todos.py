import tkinter as tk
from tkinter import messagebox, Menu
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Dictionary to map listbox items to Firestore document IDs
tasks_doc_ids = {}

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
    global tasks_doc_ids
    tasks_doc_ids.clear()
    task_var = tk.StringVar(main_frame)
    task_entry = tk.Entry(main_frame, textvariable=task_var, width=45)
    task_entry.pack(pady=10)

    listbox_tasks = tk.Listbox(main_frame, width=50, height=10)
    listbox_tasks.pack(pady=10)

    def load_tasks():
        global tasks_doc_ids
        docs = db.collection('todos').stream()
        for doc in docs:
            task = doc.to_dict()['task']
            tasks_doc_ids[listbox_tasks.size()] = doc.id
            listbox_tasks.insert(tk.END, task)

    def add_task():
        task = task_var.get()
        if task != "":
            # Manually create a new document reference with a generated ID
            doc_ref = db.collection('todos').document()
            # Set data for the new document
            doc_ref.set({'task': task, 'done': False})
            # Now you have access to the document ID
            tasks_doc_ids[listbox_tasks.size()] = doc_ref.id
            # Insert the task into the listbox
            listbox_tasks.insert(tk.END, task)
            # Clear the input field
            task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")






    add_task_btn = tk.Button(main_frame, text="Add Task", width=42, command=add_task)
    add_task_btn.pack(pady=10)

    def delete_task():
        selected_indices = listbox_tasks.curselection()
        if selected_indices:
            # Reverse the selected indices to handle multiple deletions correctly
            for index in reversed(selected_indices):
                # Convert listbox index to actual dictionary key
                actual_key = list(tasks_doc_ids.keys())[index]
                doc_id = tasks_doc_ids.pop(actual_key)
                db.collection('todos').document(doc_id).delete()
                listbox_tasks.delete(index)

            # Rebuild the tasks_doc_ids mapping
            rebuild_tasks_doc_ids()
        else:
            messagebox.showinfo("Info", "Please select a task to delete.")

    def rebuild_tasks_doc_ids():
        global tasks_doc_ids
        new_tasks_doc_ids = {}
        for index, (old_index, doc_id) in enumerate(tasks_doc_ids.items()):
            new_tasks_doc_ids[index] = doc_id
        tasks_doc_ids = new_tasks_doc_ids

            
            
            
            

    delete_task_btn = tk.Button(main_frame, text="Delete Task", width=42, command=delete_task)
    delete_task_btn.pack(pady=5)

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
