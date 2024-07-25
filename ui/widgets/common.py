import customtkinter as ctk
from PIL import Image, ImageTk

class Clock(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.clock_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.clock_frame.pack(padx=10, pady=10)
        
        try:
            self.clock_image = ctk.CTkImage(
                Image.open("media/icons/clock.png").resize((font_size, font_size)),
                size=(font_size, font_size)
            )
            self.clock_button = ctk.CTkButton(self.clock_frame, image=self.clock_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
            self.clock_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading clock icon: {e}")

    def update_time(self, time_label):
        self.clock_button.config(text=time_label)
        
class Timer(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.timer_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.timer_frame.pack(padx=10, pady=10)
        
        try:
            self.timer_image = ctk.CTkImage(
                Image.open("media/icons/timer.png").resize((font_size, font_size)),
                size=(font_size, font_size)
            )
            self.timer_button = ctk.CTkButton(self.timer_frame, image=self.timer_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
            self.timer_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading timer icon: {e}")

    def update_time(self, time_label):
        self.timer_button.config(text=time_label)
        
class StopWatch(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.stopwatch_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.stopwatch_frame.pack(padx=10, pady=10)
        
        try:
            self.stopwatch_image = ctk.CTkImage(
                Image.open("media/icons/stopwatch.png").resize((font_size, font_size)),
                size=(font_size, font_size)
            )
            self.stopwatch_button = ctk.CTkButton(self.stopwatch_frame, image=self.stopwatch_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
            self.stopwatch_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading stopwatch icon: {e}")

    def update_time(self, time_label):
        self.stopwatch_button.config(text=time_label)
        
class Alarm(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.alarm_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.alarm_frame.pack(padx=10, pady=10)
        
        try:
            self.alarm_image = ctk.CTkImage(
                Image.open("media/icons/alarm.png").resize((font_size, font_size)),
                size=(font_size, font_size)
            )
            self.alarm_button = ctk.CTkButton(self.alarm_frame, image=self.alarm_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
            self.alarm_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading alarm icon: {e}")

    def update_time(self, time_label):
        self.alarm_button.config(text=time_label)
        
class Doge(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.doge_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.doge_frame.pack(padx=10, pady=10)
        
        try:
            self.doge_image = ctk.CTkImage(
                Image.open("media/icons/doge.png").resize((font_size, font_size)),
                size=(font_size, font_size)
            )
            self.doge_button = ctk.CTkButton(self.doge_frame, image=self.doge_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
            self.doge_button.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading doge icon: {e}")

    def update_time(self, time_label):
        self.doge_button.config(text=time_label)