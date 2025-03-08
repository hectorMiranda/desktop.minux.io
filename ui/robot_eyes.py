import customtkinter as ctk
import random
import math
import time

class RobotEyes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#000000")  # Black background
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create eyes
        self.left_eye = Eye(self, "left")
        self.right_eye = Eye(self, "right")
        
        # Position eyes with more space between them
        self.left_eye.grid(row=0, column=0, padx=60, pady=60, sticky="nsew")
        self.right_eye.grid(row=0, column=1, padx=60, pady=60, sticky="nsew")
        
        # Initialize state
        self.is_blinking = False
        self.blink_start = 0
        self.blink_duration = 200  # milliseconds
        
        # Start animations
        self.animate_eyes()
        self.blink_eyes()
    
    def animate_eyes(self):
        """Smoothly move eyes every few seconds"""
        # Generate random target positions for both eyes
        target_x = random.uniform(-0.5, 0.5)
        target_y = random.uniform(-0.5, 0.5)
        
        # Create smooth movement using multiple steps
        steps = 10
        current_x = self.left_eye.current_x
        current_y = self.left_eye.current_y
        
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps
        
        def move_step(step):
            if step < steps:
                new_x = current_x + dx * (step + 1)
                new_y = current_y + dy * (step + 1)
                self.left_eye.move_to(new_x, new_y)
                self.right_eye.move_to(new_x, new_y)
                self.after(50, lambda: move_step(step + 1))
            else:
                # Schedule next animation
                delay = random.randint(2000, 5000)  # Random delay between 2-5 seconds
                self.after(delay, self.animate_eyes)
        
        move_step(0)
    
    def blink_eyes(self):
        """Periodically blink the eyes"""
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_start = time.time() * 1000
            self.left_eye.blink()
            self.right_eye.blink()
            self.after(self.blink_duration, self.finish_blink)
        
        # Schedule next blink
        delay = random.randint(3000, 7000)  # Random delay between 3-7 seconds
        self.after(delay, self.blink_eyes)
    
    def finish_blink(self):
        """Finish the blinking animation"""
        self.is_blinking = False
        self.left_eye.unblink()
        self.right_eye.unblink()

class Eye(ctk.CTkFrame):
    def __init__(self, parent, side):
        super().__init__(parent, fg_color="#222222", corner_radius=300)  # Darker gray eye socket
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create eye components
        self.white = ctk.CTkFrame(self, fg_color="white", corner_radius=280)
        self.white.place(relx=0.5, rely=0.5, relwidth=0.93, relheight=0.93, anchor="center")
        
        # Create iris (colored part)
        self.iris = ctk.CTkFrame(self.white, fg_color="#00A5FF", corner_radius=140)  # Brighter blue iris
        self.iris.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        
        # Create pupil (black center)
        self.pupil = ctk.CTkFrame(self.iris, fg_color="black", corner_radius=70)
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        
        # Add highlight (makes the eye look more realistic)
        self.highlight = ctk.CTkFrame(self.iris, fg_color="white", corner_radius=20)
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.15, relheight=0.15, anchor="center")
        
        # Initialize position
        self.current_x = 0
        self.current_y = 0
        
        # Store original heights for blinking
        self.original_height = 0.93
    
    def move_to(self, target_x, target_y):
        """Move the eye to look at a target position"""
        # Calculate new position (limit movement range)
        new_x = max(-0.2, min(0.2, target_x))
        new_y = max(-0.2, min(0.2, target_y))
        
        # Update iris position
        self.iris.place(
            relx=0.5 + new_x,
            rely=0.5 + new_y,
            relwidth=0.5,
            relheight=0.5,
            anchor="center"
        )
        
        # Update pupil and highlight positions
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.15, relheight=0.15, anchor="center")
        
        # Store current position
        self.current_x = new_x
        self.current_y = new_y
    
    def blink(self):
        """Start blinking animation"""
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.93,
            relheight=0.1,  # Squish the eye
            anchor="center"
        )
    
    def unblink(self):
        """End blinking animation"""
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.93,
            relheight=self.original_height,
            anchor="center"
        )

def main():
    # Create and configure the root window
    root = ctk.CTk()
    root.title("Robot Eyes")
    
    # Configure for fullscreen
    root.attributes('-fullscreen', True)
    root.configure(fg_color="black")
    
    # Allow quitting with ESC
    root.bind('<Escape>', lambda e: root.quit())
    
    # Create and pack the robot eyes
    eyes = RobotEyes(root)
    eyes.pack(expand=True, fill="both")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 