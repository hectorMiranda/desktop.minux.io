import customtkinter as ctk
import sys
import logging
from .welcome import WelcomeScreen
from .robot_eyes import RobotEyes

class App(ctk.CTk):
    def __init__(self, working_dir=None):
        super().__init__()
        
        # Check if we're in PI mode
        self.pi_mode = "-pi" in sys.argv
        
        if self.pi_mode:
            # Disable debug logging in PI mode
            logging.getLogger().setLevel(logging.WARNING)
            
            # Start in fullscreen for PI mode
            self.attributes('-fullscreen', True)
            self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))
            
            # Configure window for robot eyes
            self.configure(fg_color="black")  # Set background to black
            
            # Create and show robot eyes
            self.robot_eyes = RobotEyes(self)
            self.robot_eyes.pack(expand=True, fill="both", padx=20, pady=20)
        else:
            # Normal mode - show welcome screen or workspace
            self.title("Minux")
            self.geometry("1200x800")
            
            if working_dir:
                # TODO: Initialize workspace with working_dir
                pass
            else:
                # Show welcome screen
                welcome = WelcomeScreen(self, self.handle_welcome_action)
                welcome.pack(expand=True, fill="both")
    
    def handle_welcome_action(self, action):
        """Handle actions from welcome screen"""
        action_type = action[0] if isinstance(action, tuple) else action
        action_data = action[1] if isinstance(action, tuple) and len(action) > 1 else None
        
        if action_type == "open_todo":
            # TODO: Handle opening todo
            pass
// ... existing code ...