import tkinter as tk
from tkinter import messagebox, Menu

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

    def add_task():
        task = task_var.get()
        if task != "":
            listbox_tasks.insert(tk.END, task)
            task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    add_task_btn = tk.Button(main_frame, text="Add Task", width=42, command=add_task)
    add_task_btn.pack(pady=10)

    def mark_done():
        selected_task_idx = listbox_tasks.curselection()
        if selected_task_idx:
            current_task = listbox_tasks.get(selected_task_idx[0])
            listbox_tasks.delete(selected_task_idx)
            listbox_tasks.insert(selected_task_idx, "Done: " + current_task)
        else:
            messagebox.showinfo("Info", "Please select a task to mark as done.")

    done_task_btn = tk.Button(main_frame, text="Mark as Done", width=42, command=mark_done)
    done_task_btn.pack(pady=5)

    def delete_task():
        selected_task_idx = listbox_tasks.curselection()
        if selected_task_idx:
            listbox_tasks.delete(selected_task_idx[0])
        else:
            messagebox.showinfo("Info", "Please select a task to delete.")

    delete_task_btn = tk.Button(main_frame, text="Delete Task", width=42, command=delete_task)
    delete_task_btn.pack(pady=5)

root = tk.Tk()
root.title("Control Center")

# Make the window full-screen
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
