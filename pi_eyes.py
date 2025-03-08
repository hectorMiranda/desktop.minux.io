import customtkinter as ctk
from ui.robot_eyes import RobotEyes

def main():
    # Create the root window
    root = ctk.CTk()
    
    # Configure for fullscreen
    root.attributes('-fullscreen', True)
    root.configure(fg_color="black")  # Set background to black
    root.bind('<Escape>', lambda e: root.quit())  # Allow quitting with ESC
    
    # Create and pack the robot eyes
    eyes = RobotEyes(root)
    eyes.pack(expand=True, fill="both", padx=20, pady=20)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 