#!/usr/bin/env python3
import customtkinter as ctk
from ui.robot_eyes import RobotEyes
import sys

def main():
    # Create and configure the root window
    root = ctk.CTk()
    
    # Hide the title bar completely
    root.overrideredirect(True)
    
    # Make it cover the full screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Configure window
    root.configure(fg_color="black")
    
    # Allow quitting with ESC
    def quit_app(event=None):
        root.destroy()
        sys.exit(0)
    
    root.bind('<Escape>', quit_app)
    
    # Create and pack the robot eyes
    eyes = RobotEyes(root)
    eyes.pack(expand=True, fill="both", padx=100, pady=100)  # Larger padding for better centering
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 