import customtkinter as ctk
from PIL import Image, ImageTk

class Clock(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.clock_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        self.clock_frame.pack(padx=10, pady=10)
        
        try:
            icon_size = max(24, font_size * 2)  # Ensure minimum size of 24px
            self.clock_image = ctk.CTkImage(
                light_image=Image.open("media/icons/clock.png"),
                dark_image=Image.open("media/icons/clock.png"),
                size=(icon_size, icon_size)
            )
            self.clock_button = ctk.CTkButton(
                self.clock_frame, 
                image=self.clock_image,
                text="",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        except Exception as e:
            print(f"Error loading clock icon: {e}")
            self.clock_button = ctk.CTkButton(
                self.clock_frame,
                text="⏰",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        self.clock_button.pack(side="left", padx=5)

    def update_time(self, time_label):
        self.clock_button.configure(text=time_label)
        
class Timer(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.timer_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        self.timer_frame.pack(padx=10, pady=10)
        
        try:
            icon_size = max(24, font_size * 2)  # Ensure minimum size of 24px
            self.timer_image = ctk.CTkImage(
                light_image=Image.open("media/icons/timer.png"),
                dark_image=Image.open("media/icons/timer.png"),
                size=(icon_size, icon_size)
            )
            self.timer_button = ctk.CTkButton(
                self.timer_frame,
                image=self.timer_image,
                text="",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        except Exception as e:
            print(f"Error loading timer icon: {e}")
            self.timer_button = ctk.CTkButton(
                self.timer_frame,
                text="⏲",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        self.timer_button.pack(side="left", padx=5)

    def update_time(self, time_label):
        self.timer_button.configure(text=time_label)
        
class StopWatch(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.stopwatch_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        self.stopwatch_frame.pack(padx=10, pady=10)
        
        try:
            icon_size = max(24, font_size * 2)  # Ensure minimum size of 24px
            self.stopwatch_image = ctk.CTkImage(
                light_image=Image.open("media/icons/stopwatch.png"),
                dark_image=Image.open("media/icons/stopwatch.png"),
                size=(icon_size, icon_size)
            )
            self.stopwatch_button = ctk.CTkButton(
                self.stopwatch_frame,
                image=self.stopwatch_image,
                text="",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        except Exception as e:
            print(f"Error loading stopwatch icon: {e}")
            self.stopwatch_button = ctk.CTkButton(
                self.stopwatch_frame,
                text="⏱",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        self.stopwatch_button.pack(side="left", padx=5)

    def update_time(self, time_label):
        self.stopwatch_button.configure(text=time_label)
        
class Alarm(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.alarm_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        self.alarm_frame.pack(padx=10, pady=10)
        
        try:
            icon_size = max(24, font_size * 2)  # Ensure minimum size of 24px
            self.alarm_image = ctk.CTkImage(
                light_image=Image.open("media/icons/alarm.png"),
                dark_image=Image.open("media/icons/alarm.png"),
                size=(icon_size, icon_size)
            )
            self.alarm_button = ctk.CTkButton(
                self.alarm_frame,
                image=self.alarm_image,
                text="",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        except Exception as e:
            print(f"Error loading alarm icon: {e}")
            self.alarm_button = ctk.CTkButton(
                self.alarm_frame,
                text="🔔",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        self.alarm_button.pack(side="left", padx=5)

    def update_time(self, time_label):
        self.alarm_button.configure(text=time_label)
        
class Doge(ctk.CTkFrame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent)
        self.doge_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        self.doge_frame.pack(padx=10, pady=10)
        
        try:
            icon_size = max(24, font_size * 2)  # Ensure minimum size of 24px
            self.doge_image = ctk.CTkImage(
                light_image=Image.open("media/icons/doge.png"),
                dark_image=Image.open("media/icons/doge.png"),
                size=(icon_size, icon_size)
            )
            self.doge_button = ctk.CTkButton(
                self.doge_frame,
                image=self.doge_image,
                text="",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        except Exception as e:
            print(f"Error loading doge icon: {e}")
            self.doge_button = ctk.CTkButton(
                self.doge_frame,
                text="🐕",
                fg_color="transparent",
                hover_color="gray20",
                corner_radius=0,
                width=icon_size,
                height=icon_size
            )
        self.doge_button.pack(side="left", padx=5)

    def update_time(self, time_label):
        self.doge_button.configure(text=time_label)