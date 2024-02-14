import tkinter as tk
from tkinter import ttk, messagebox, Menu
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
import folium
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import random



load_dotenv()

WINDOW_TITLE = os.getenv('WINDOW_TITLE', 'Default Title')
WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE', 'Welcome!')
SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', 'service_account_key.json')





firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH))
db = firestore.client()


def show_map_qt(map_file):
    app = QApplication([])
    main_window = QMainWindow()
    web_view = QWebEngineView()
    web_view.load(QUrl.fromLocalFile(os.path.abspath(map_file)))
    main_window.setCentralWidget(web_view)
    main_window.show()
    app.exec_()
    
def show_map():
    clear_frame()

    # Center the map on the state of Veracruz
    veracruz_center = [19.1723, -96.1332]
    m = folium.Map(location=veracruz_center, zoom_start=8)

    # Top 20 most important cities in the state of Veracruz, Mexico

    cities = [
        {"name": "Veracruz", "coordinates": [19.173773, -96.134224]},
        {"name": "Xalapa", "coordinates": [19.543775, -96.910181]},
        {"name": "Coatzacoalcos", "coordinates": [18.134478, -94.458986]},
        {"name": "Poza Rica", "coordinates": [20.533153, -97.459461]},
        {"name": "Orizaba", "coordinates": [18.847231, -97.099754]},
        {"name": "Córdoba", "coordinates": [18.894303, -96.935250]},
        {"name": "Minatitlán", "coordinates": [17.989169, -94.558586]},
        {"name": "Papantla", "coordinates": [20.456698, -97.315270]},
        {"name": "San Andrés Tuxtla", "coordinates": [18.443051, -95.213547]},
        {"name": "Tuxpan", "coordinates": [20.956928, -97.407086]},
        {"name": "Martínez de la Torre", "coordinates": [20.070123, -97.060198]},
        {"name": "Boca del Río", "coordinates": [19.100533, -96.106003]},
        {"name": "Cosamaloapan", "coordinates": [18.360296, -95.797776]},
        {"name": "Coatepec", "coordinates": [19.452098, -96.961444]},
        {"name": "Tierra Blanca", "coordinates": [18.455750, -96.350240]},
        {"name": "Alvarado", "coordinates": [18.775949, -95.764993]},
        {"name": "Acayucan", "coordinates": [17.950141, -94.914499]},
        {"name": "Perote", "coordinates": [19.566519, -97.239818]},
        {"name": "Panuco", "coordinates": [22.052490, -98.188745]},
        {"name": "Fortín", "coordinates": [18.898176, -96.991195]},
    ]

    for city in cities:
        completion_percentage = random.randint(0, 100)  # Generate a random completion percentage
        popup_text = f"{city['name']} - Completion: {completion_percentage}%"
        folium.Marker(
            city["coordinates"], 
            popup=popup_text, 
            icon=folium.Icon(color='red')
        ).add_to(m)

    # Save the map as an HTML file
    map_file = 'map.html'
    m.save(map_file)

    # Use PyQt5 to display the map
    show_map_qt(map_file)




def show_welcome():
    clear_frame()

    # Assuming a grid layout of 2x3 for simplicity
    rows, cols = 2, 3
    for index, item in enumerate(dashboard_items):
        row, col = divmod(index, cols)
        img = tk.PhotoImage(file=item["icon"]).subsample(3, 3)  
        # Button with icon
        btn = tk.Button(main_frame, image=img, command=item["action"])
        btn.image = img  # Keep a reference
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    # Adjust grid weights to expand cells to available space
    for i in range(rows):
        main_frame.rowconfigure(i, weight=1)
    for j in range(cols):
        main_frame.columnconfigure(j, weight=1)
        

    
def show_coming_soon():
    messagebox.showinfo("Coming Soon", "This feature is coming soon!")


def open_tasks():
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
    
    
    def toggle_done(event):
        column = tree.identify_column(event.x)
        if column == "#2":  # Assuming "#2" is the "Done" column
            item_id = tree.identify_row(event.y)
            if item_id:  # Ensure item_id is not an empty string
                task_info = db.collection('todos').document(item_id).get().to_dict()
                if task_info:  # Additional check if task_info is successfully retrieved
                    new_status = not task_info.get('done', False)
                    update_data = {'done': new_status}
                    if new_status:  # If marking as done, add the timestamp
                        update_data['completed_date'] = firestore.SERVER_TIMESTAMP
                    db.collection('todos').document(item_id).update(update_data)
                    load_tasks()  # Reload tasks to reflect changes

    
    tree.bind("<Button-1>", toggle_done)
    

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


def navigate_to_dashboard(index):
    dashboard_items[index]["action"]()

def create_toolbar(toolbar_frame):
    for index, item in enumerate(dashboard_items):
        img = tk.PhotoImage(file=item["icon"]).subsample(10, 10)  # Adjust subsample factors to fit your toolbar
        btn = tk.Button(toolbar_frame, image=img, command=lambda idx=index: navigate_to_dashboard(idx))
        btn.image = img
        btn.grid(row=0, column=index, padx=10, pady=5)
        
dashboard_items = [
    {"name": "Home", "icon": "icons/home.png", "action": show_welcome},
    {"name": "Tasks", "icon": "icons/tasks.png", "action": open_tasks},
    {"name": "Maps", "icon": "icons/reports.png", "action": show_map},
    {"name": "AI", "icon": "icons/ai.png", "action": lambda: messagebox.showinfo("AI", "Coming Soon")},
    {"name": "Help", "icon": "icons/help.png", "action": lambda: messagebox.showinfo("Help", "Coming Soon")},
]


root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(f"{os.getenv('WINDOW_WIDTH', '800')}x{os.getenv('WINDOW_HEIGHT', '600')}")
root.attributes('-fullscreen', False)
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

menu_bar = Menu(root)
root.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Welcome", command=show_welcome)
file_menu.add_command(label="Tasks", command=open_tasks)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)


# Edit Menu
edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo", command=show_coming_soon)
edit_menu.add_command(label="Redo", command=show_coming_soon)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Reports Menu
reports_menu = Menu(menu_bar, tearoff=0)
reports_menu.add_command(label="Monthly Report", command=show_coming_soon)
reports_menu.add_command(label="Annual Report", command=show_coming_soon)
menu_bar.add_cascade(label="Reports", menu=reports_menu)

# AI Menu
ai_menu = Menu(menu_bar, tearoff=0)
ai_menu.add_command(label="Data Analysis", command=show_coming_soon)
ai_menu.add_command(label="Predictive Maintenance", command=show_coming_soon)
menu_bar.add_cascade(label="AI", menu=ai_menu)

# Help Menu
help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Documentation", command=show_coming_soon)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", os.getenv('ABOUT_MESSAGE', 'Control center demo app for a Consulting Company')))
menu_bar.add_cascade(label="Help", menu=help_menu)

# Create a toolbar frame
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(side="top", fill="x")

# Create the toolbar
create_toolbar(toolbar_frame)


main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

show_welcome()

root.mainloop()
