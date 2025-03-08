import customtkinter as ctk
import random
import math
import time
from typing import Tuple, Dict

class Emotion:
    def __init__(self, iris_color: str, pupil_scale: float, eye_scale: float, blink_speed: int = 200):
        self.iris_color = iris_color
        self.pupil_scale = pupil_scale  # Scale of pupil relative to iris
        self.eye_scale = eye_scale      # Scale of iris relative to eye
        self.blink_speed = blink_speed  # Blink animation duration in ms

class RobotEyes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#000000")
        
        # Define emotions
        self.emotions = {
            "normal": Emotion("#00A5FF", 0.5, 0.5),
            "happy": Emotion("#50C878", 0.4, 0.45, 150),  # Green, smaller pupils
            "sad": Emotion("#4169E1", 0.5, 0.4, 300),     # Royal blue, droopy eyes
            "angry": Emotion("#FF4500", 0.6, 0.6, 100),   # Red-orange, large eyes
            "surprised": Emotion("#FFD700", 0.7, 0.7, 50), # Gold, very large eyes
            "tired": Emotion("#778899", 0.3, 0.4, 400),   # Gray-blue, small pupils
            "danger": Emotion("#FF0000", 0.8, 0.6, 100),  # Red, large pupils
            "curious": Emotion("#9370DB", 0.45, 0.55, 200), # Purple, medium eyes
            "love": Emotion("#FF69B4", 0.4, 0.6, 150),    # Pink, heart-shaped
        }
        
        self.current_emotion = "normal"
        self.transition_time = 500  # Time for emotion transitions in ms
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create eyes
        self.left_eye = Eye(self, "left")
        self.right_eye = Eye(self, "right")
        
        # Position eyes with more space between them
        self.left_eye.grid(row=0, column=0, padx=80, pady=80, sticky="nsew")
        self.right_eye.grid(row=0, column=1, padx=80, pady=80, sticky="nsew")
        
        # Initialize state
        self.is_blinking = False
        self.blink_start = 0
        self.blink_duration = 200
        
        # Start animations
        self.animate_eyes()
        self.blink_eyes()
        self.change_emotion()
    
    def animate_eyes(self):
        """Smoothly move eyes every few seconds"""
        if self.current_emotion == "surprised":
            # Wide-eyed stare
            target_x = 0
            target_y = 0
        elif self.current_emotion == "tired":
            # Droopy eyes
            target_y = 0.2
            target_x = random.uniform(-0.1, 0.1)
        elif self.current_emotion == "love":
            # Gentle upward gaze
            target_y = -0.1
            target_x = random.uniform(-0.1, 0.1)
        else:
            # Normal random movement
            target_x = random.uniform(-0.5, 0.5)
            target_y = random.uniform(-0.5, 0.5)
        
        # Create smooth movement using multiple steps
        steps = 15
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
                self.after(30, lambda: move_step(step + 1))
            else:
                # Schedule next animation
                delay = random.randint(1000, 3000)
                self.after(delay, self.animate_eyes)
        
        move_step(0)
    
    def change_emotion(self):
        """Randomly change emotional state"""
        # Choose a new random emotion different from current
        emotions = list(self.emotions.keys())
        emotions.remove(self.current_emotion)
        new_emotion = random.choice(emotions)
        
        # Get the emotion settings
        emotion = self.emotions[new_emotion]
        
        # Smoothly transition to new emotion
        self.left_eye.transition_to_emotion(emotion)
        self.right_eye.transition_to_emotion(emotion)
        
        # Update current emotion
        self.current_emotion = new_emotion
        
        # Schedule next emotion change
        delay = random.randint(5000, 15000)  # Change emotion every 5-15 seconds
        self.after(delay, self.change_emotion)
    
    def blink_eyes(self):
        """Periodically blink the eyes"""
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_start = time.time() * 1000
            self.left_eye.blink()
            self.right_eye.blink()
            # Use emotion-specific blink speed
            blink_speed = self.emotions[self.current_emotion].blink_speed
            self.after(blink_speed, self.finish_blink)
        
        # Schedule next blink
        if self.current_emotion == "tired":
            delay = random.randint(1000, 3000)  # Blink more frequently when tired
        else:
            delay = random.randint(3000, 7000)
        self.after(delay, self.blink_eyes)
    
    def finish_blink(self):
        """Finish the blinking animation"""
        self.is_blinking = False
        self.left_eye.unblink()
        self.right_eye.unblink()

class Eye(ctk.CTkFrame):
    def __init__(self, parent, side):
        super().__init__(parent, fg_color="black", corner_radius=300)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create eye components with smoother corners
        self.white = ctk.CTkFrame(self, fg_color="white", corner_radius=280)
        self.white.place(relx=0.5, rely=0.5, relwidth=0.93, relheight=0.93, anchor="center")
        
        # Create iris (colored part)
        self.iris = ctk.CTkFrame(self.white, fg_color="#00A5FF", corner_radius=140)
        self.iris.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        
        # Create pupil (black center)
        self.pupil = ctk.CTkFrame(self.iris, fg_color="black", corner_radius=70)
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        
        # Add highlight (makes the eye look more realistic)
        self.highlight = ctk.CTkFrame(self.iris, fg_color="white", corner_radius=20)
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.15, relheight=0.15, anchor="center")
        
        # Add secondary highlight for more depth
        self.highlight2 = ctk.CTkFrame(self.iris, fg_color="white", corner_radius=10)
        self.highlight2.place(relx=0.3, rely=0.7, relwidth=0.1, relheight=0.1, anchor="center")
        
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
        
        # Update pupil and highlights
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.15, relheight=0.15, anchor="center")
        self.highlight2.place(relx=0.3, rely=0.7, relwidth=0.1, relheight=0.1, anchor="center")
        
        # Store current position
        self.current_x = new_x
        self.current_y = new_y
    
    def transition_to_emotion(self, emotion: Emotion):
        """Smoothly transition to a new emotional state"""
        # Update iris color
        self.iris.configure(fg_color=emotion.iris_color)
        
        # Update sizes
        self.iris.place(
            relx=0.5 + self.current_x,
            rely=0.5 + self.current_y,
            relwidth=emotion.eye_scale,
            relheight=emotion.eye_scale,
            anchor="center"
        )
        
        self.pupil.place(
            relx=0.5,
            rely=0.5,
            relwidth=emotion.pupil_scale,
            relheight=emotion.pupil_scale,
            anchor="center"
        )
    
    def blink(self):
        """Start blinking animation"""
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.93,
            relheight=0.1,
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
    
    # Hide the title bar completely
    root.overrideredirect(True)
    
    # Make it cover the full screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Configure window
    root.configure(fg_color="black")
    
    # Allow quitting with ESC
    root.bind('<Escape>', lambda e: root.quit())
    
    # Create and pack the robot eyes
    eyes = RobotEyes(root)
    eyes.pack(expand=True, fill="both", padx=40, pady=40)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 