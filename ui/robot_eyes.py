import customtkinter as ctk
import random
import math
import time
from typing import Tuple, Dict

class Emotion:
    def __init__(self, iris_color: str, pupil_scale: float, eye_scale: float, 
                 blink_speed: int = 200, eyebrows: bool = False, 
                 eyebrow_angle: float = 0, tired: bool = False):
        self.iris_color = iris_color
        self.pupil_scale = pupil_scale
        self.eye_scale = eye_scale
        self.blink_speed = blink_speed
        self.eyebrows = eyebrows
        self.eyebrow_angle = eyebrow_angle  # Angle in degrees
        self.tired = tired

class RobotEyes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#000000")
        
        # Define emotions
        self.emotions = {
            "normal": Emotion("#4B9EEB", 0.45, 0.6),                          # Friendly blue
            "happy": Emotion("#4B9EEB", 0.3, 0.5, 150, True, -15),           # Smaller pupils, raised eyebrows
            "sad": Emotion("#4B9EEB", 0.4, 0.5, 300, True, 15),              # Blue, droopy eyebrows
            "angry": Emotion("#E86D6D", 0.5, 0.65, 100, True, 45),           # Red, angled eyebrows
            "surprised": Emotion("#4B9EEB", 0.6, 0.7, 50, True, -30),        # Large eyes, raised eyebrows
            "tired": Emotion("#4B9EEB", 0.4, 0.4, 400, False, 0, True),      # Smaller eyes with dark circles
            "sleepy": Emotion("#4B9EEB", 0.3, 0.3, 500, False, 0, True),     # Very small eyes with dark circles
            "excited": Emotion("#4B9EEB", 0.4, 0.7, 100, True, -20),         # Large eyes, raised eyebrows
            "confused": Emotion("#4B9EEB", 0.45, 0.6, 200, True, -10),       # One eyebrow up
        }
        
        self.current_emotion = "normal"
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create eyes
        self.left_eye = Eye(self, "left")
        self.right_eye = Eye(self, "right")
        
        # Position eyes
        self.left_eye.grid(row=0, column=0, padx=60, pady=60, sticky="nsew")
        self.right_eye.grid(row=0, column=1, padx=60, pady=60, sticky="nsew")
        
        # Initialize state
        self.is_blinking = False
        
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
        elif self.current_emotion == "tired" or self.current_emotion == "sleepy":
            # Droopy eyes
            target_y = 0.2
            target_x = random.uniform(-0.1, 0.1)
        elif self.current_emotion == "confused":
            # Look around more randomly
            target_x = random.uniform(-0.3, 0.3)
            target_y = random.uniform(-0.3, 0.3)
        else:
            # Normal random movement
            target_x = random.uniform(-0.2, 0.2)
            target_y = random.uniform(-0.2, 0.2)
        
        # Create smooth movement using multiple steps
        steps = 20
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
                if self.current_emotion in ["tired", "sleepy"]:
                    delay = random.randint(2000, 4000)  # Move less when tired
                else:
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
            self.left_eye.blink()
            self.right_eye.blink()
            # Use emotion-specific blink speed
            blink_speed = self.emotions[self.current_emotion].blink_speed
            self.after(blink_speed, self.finish_blink)
        
        # Schedule next blink
        if self.current_emotion in ["tired", "sleepy"]:
            delay = random.randint(1000, 2000)  # Blink more frequently when tired
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
        super().__init__(parent, fg_color="black")
        
        self.side = side
        
        # Create the white part of the eye
        self.white = ctk.CTkFrame(self, fg_color="white", corner_radius=300)
        self.white.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center")
        
        # Create iris
        self.iris = ctk.CTkFrame(self.white, fg_color="#4B9EEB", corner_radius=300)
        self.iris.place(relx=0.5, rely=0.5, relwidth=0.6, relheight=0.6, anchor="center")
        
        # Create pupil
        self.pupil = ctk.CTkFrame(self.iris, fg_color="black", corner_radius=300)
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.45, relheight=0.45, anchor="center")
        
        # Create highlight
        self.highlight = ctk.CTkFrame(self.iris, fg_color="white", corner_radius=300)
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.2, relheight=0.2, anchor="center")
        
        # Create eyebrow (hidden by default)
        self.eyebrow = ctk.CTkFrame(self, fg_color="#333333", corner_radius=5)
        self.eyebrow.place_forget()
        
        # Create tired circles (hidden by default)
        self.tired_circle = ctk.CTkFrame(self, fg_color="#D3D3D3", corner_radius=300)
        self.tired_circle.place_forget()
        
        # Initialize position
        self.current_x = 0
        self.current_y = 0
        self.original_height = 0.9
    
    def move_to(self, target_x, target_y):
        """Move the eye smoothly"""
        new_x = max(-0.2, min(0.2, target_x))
        new_y = max(-0.2, min(0.2, target_y))
        
        # Move iris and contents
        self.iris.place(
            relx=0.5 + new_x,
            rely=0.5 + new_y,
            relwidth=0.6,
            relheight=0.6,
            anchor="center"
        )
        
        # Move pupil and highlight
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.45, relheight=0.45, anchor="center")
        self.highlight.place(relx=0.7, rely=0.3, relwidth=0.2, relheight=0.2, anchor="center")
        
        self.current_x = new_x
        self.current_y = new_y
    
    def transition_to_emotion(self, emotion: Emotion):
        """Transition to a new emotional state"""
        # Update iris color
        self.iris.configure(fg_color=emotion.iris_color)
        
        # Update eye size
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=emotion.eye_scale,
            relheight=emotion.eye_scale,
            anchor="center"
        )
        
        # Update pupil size
        self.pupil.place(
            relx=0.5,
            rely=0.5,
            relwidth=emotion.pupil_scale,
            relheight=emotion.pupil_scale,
            anchor="center"
        )
        
        # Handle eyebrows
        if emotion.eyebrows:
            eyebrow_width = 0.8
            eyebrow_height = 0.1
            eyebrow_y = 0.15  # Distance above eye
            
            if self.side == "left":
                if emotion.eyebrow_angle > 0:  # Sad or angry
                    transform_angle = emotion.eyebrow_angle
                else:  # Happy or surprised
                    transform_angle = -emotion.eyebrow_angle
            else:
                if emotion.eyebrow_angle > 0:  # Sad or angry
                    transform_angle = -emotion.eyebrow_angle
                else:  # Happy or surprised
                    transform_angle = emotion.eyebrow_angle
            
            self.eyebrow.configure(fg_color="#333333")
            self.eyebrow.place(
                relx=0.5,
                rely=0.2,
                relwidth=eyebrow_width,
                relheight=eyebrow_height,
                anchor="center"
            )
        else:
            self.eyebrow.place_forget()
        
        # Handle tired appearance
        if emotion.tired:
            self.tired_circle.configure(fg_color="#D3D3D3")
            self.tired_circle.place(
                relx=0.5,
                rely=0.8,
                relwidth=0.7,
                relheight=0.2,
                anchor="center"
            )
        else:
            self.tired_circle.place_forget()
    
    def blink(self):
        """Cute blinking animation"""
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.9,
            relheight=0.1,
            anchor="center"
        )
    
    def unblink(self):
        """Return to normal eye state"""
        self.white.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.9,
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