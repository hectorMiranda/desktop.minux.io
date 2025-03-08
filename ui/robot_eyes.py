import customtkinter as ctk
import random
import math
import time
from typing import Tuple, Dict

class Emotion:
    def __init__(self, iris_color: str, secondary_color: str, pupil_scale: float, eye_scale: float, blink_speed: int = 200):
        self.iris_color = iris_color
        self.secondary_color = secondary_color  # For the hexagonal pattern
        self.pupil_scale = pupil_scale
        self.eye_scale = eye_scale
        self.blink_speed = blink_speed

class RobotEyes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#000000")
        
        # Define emotions with cybernetic color schemes
        self.emotions = {
            "normal": Emotion("#00FFFF", "#007777", 0.5, 0.5),           # Cyan
            "happy": Emotion("#00FF00", "#007700", 0.4, 0.45, 150),      # Bright green
            "sad": Emotion("#0077FF", "#003377", 0.5, 0.4, 300),         # Deep blue
            "angry": Emotion("#FF3300", "#771100", 0.6, 0.6, 100),       # Bright red
            "surprised": Emotion("#FFFF00", "#777700", 0.7, 0.7, 50),    # Yellow
            "tired": Emotion("#777777", "#333333", 0.3, 0.4, 400),       # Gray
            "danger": Emotion("#FF0000", "#770000", 0.8, 0.6, 100),      # Pure red
            "scanning": Emotion("#00FF77", "#007733", 0.45, 0.55, 200),  # Scanner green
            "processing": Emotion("#FF00FF", "#770077", 0.4, 0.6, 150),  # Processing purple
        }
        
        self.current_emotion = "normal"
        self.transition_time = 500
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create eyes
        self.left_eye = Eye(self, "left")
        self.right_eye = Eye(self, "right")
        
        # Position eyes
        self.left_eye.grid(row=0, column=0, padx=100, pady=100, sticky="nsew")
        self.right_eye.grid(row=0, column=1, padx=100, pady=100, sticky="nsew")
        
        # Initialize state
        self.is_blinking = False
        self.scanning_mode = False
        
        # Start animations
        self.animate_eyes()
        self.blink_eyes()
        self.change_emotion()
        self.pulse_effect()

    def pulse_effect(self):
        """Create a subtle pulsing effect"""
        for eye in [self.left_eye, self.right_eye]:
            eye.pulse()
        self.after(2000, self.pulse_effect)

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
        super().__init__(parent, fg_color="black")
        
        # Create the outer hexagonal frame
        self.outer_frame = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0)
        self.outer_frame.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.95, anchor="center")
        
        # Create mechanical elements (decorative lines)
        self.create_mechanical_elements()
        
        # Create the main eye components
        self.eye_frame = ctk.CTkFrame(self.outer_frame, fg_color="#222222", corner_radius=0)
        self.eye_frame.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.8, anchor="center")
        
        # Create iris (LED ring effect)
        self.iris = ctk.CTkFrame(self.eye_frame, fg_color="#00FFFF", corner_radius=0)
        self.iris.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.7, anchor="center")
        
        # Create inner mechanical rings
        self.create_iris_rings()
        
        # Create pupil (scanner effect)
        self.pupil = ctk.CTkFrame(self.iris, fg_color="black", corner_radius=0)
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        
        # Create scanner line
        self.scanner = ctk.CTkFrame(self.pupil, fg_color="#00FFFF", corner_radius=0)
        self.scanner.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.05, anchor="center")
        
        # Initialize position and state
        self.current_x = 0
        self.current_y = 0
        self.pulse_state = 0
        self.original_height = 0.8
    
    def create_mechanical_elements(self):
        """Create decorative mechanical elements"""
        # Create corner brackets
        for i in range(4):
            angle = i * 90
            line = ctk.CTkFrame(self.outer_frame, fg_color="#333333", corner_radius=0)
            if i % 2 == 0:
                line.place(relx=0.1 + (i//2)*0.8, rely=0.05, relwidth=0.02, relheight=0.2)
            else:
                line.place(relx=0.05, rely=0.1 + ((i-1)//2)*0.8, relwidth=0.2, relheight=0.02)
    
    def create_iris_rings(self):
        """Create concentric mechanical rings in the iris"""
        # Create multiple thin rings
        for i in range(3):
            ring = ctk.CTkFrame(self.iris, fg_color="#111111", corner_radius=0)
            size = 0.8 - (i * 0.2)
            ring.place(relx=0.5, rely=0.5, relwidth=size, relheight=size, anchor="center")
    
    def pulse(self):
        """Create a subtle pulsing effect"""
        self.pulse_state = (self.pulse_state + 1) % 100
        brightness = abs(math.sin(self.pulse_state / 50 * math.pi))
        
        # Update iris brightness
        current_color = self.iris.cget("fg_color")
        if isinstance(current_color, str):
            base_color = current_color
        else:
            base_color = current_color[1]  # Use the non-dark mode color
        
        # Create a dimmer version of the color
        r = int(int(base_color[1:3], 16) * brightness)
        g = int(int(base_color[3:5], 16) * brightness)
        b = int(int(base_color[5:7], 16) * brightness)
        
        new_color = f"#{r:02x}{g:02x}{b:02x}"
        self.iris.configure(fg_color=new_color)
    
    def move_to(self, target_x, target_y):
        """Move the eye with mechanical precision"""
        new_x = max(-0.15, min(0.15, target_x))
        new_y = max(-0.15, min(0.15, target_y))
        
        # Move iris with a slight mechanical delay
        self.iris.place(
            relx=0.5 + new_x,
            rely=0.5 + new_y,
            relwidth=0.7,
            relheight=0.7,
            anchor="center"
        )
        
        # Move pupil and scanner
        self.pupil.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5, anchor="center")
        self.scanner.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.05, anchor="center")
        
        self.current_x = new_x
        self.current_y = new_y
    
    def transition_to_emotion(self, emotion: Emotion):
        """Transition to new emotion with mechanical effect"""
        # Update colors with LED-like effect
        self.iris.configure(fg_color=emotion.iris_color)
        self.scanner.configure(fg_color=emotion.secondary_color)
        
        # Update sizes with mechanical precision
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
        """Mechanical shutter-like blink"""
        self.eye_frame.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.8,
            relheight=0.1,
            anchor="center"
        )
    
    def unblink(self):
        """Mechanical shutter-like unblink"""
        self.eye_frame.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.8,
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