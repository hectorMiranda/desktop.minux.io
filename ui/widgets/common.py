import customtkinter as ctk
from PIL import Image, ImageTk

class Clock:
    def __init__(self, parent, font_size):
        self.clock_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.clock_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.clock_frame.grid_columnconfigure(1, weight=1)
        self.clock_frame.grid_propagate(False)

        self.clock_image = ctk.CTkImage(Image.open("./media/icons/clock.png").resize((font_size, font_size)))

        self.clock_label = ctk.CTkLabel(self.clock_frame, text="00:00:00", font_size=font_size)
        self.clock_label.grid(row=0, column=0, padx=1, pady=1)
        self.clock_button = ctk.CTkButton(self.clock_frame, image=self.clock_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
        self.clock_button.grid(row=0, column=2, padx=1, pady=1, sticky="w")

    def update_time(self, time_label):
        self.clock_label.config(text=time_label)
        
class Timer:
    def __init__(self, parent, font_size):
        self.timer_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.timer_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.timer_frame.grid_columnconfigure(1, weight=1)
        self.timer_frame.grid_propagate(False)

        self.timer_image = ctk.CTkImage(Image.open("./media/icons/timer.png").resize((font_size, font_size)))

        self.timer_label = ctk.CTkLabel(self.timer_frame, text="00:00:00", font_size=font_size)
        self.timer_label.grid(row=0, column=0, padx=1, pady=1)
        self.timer_button = ctk.CTkButton(self.timer_frame, image=self.timer_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
        self.timer_button.grid(row=0, column=2, padx=1, pady=1, sticky="w")

    def update_time(self, time_label):
        self.timer_label.config(text=time_label)
        
class StopWatch:
    def __init__(self, parent, font_size):
        self.stopwatch_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.stopwatch_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.stopwatch_frame.grid_columnconfigure(1, weight=1)
        self.stopwatch_frame.grid_propagate(False)

        self.stopwatch_image = ctk.CTkImage(Image.open("./media/icons/stopwatch.png").resize((font_size, font_size)))

        self.stopwatch_label = ctk.CTkLabel(self.stopwatch_frame, text="00:00:00", font_size=font_size)
        self.stopwatch_label.grid(row=0, column=0, padx=1, pady=1)
        self.stopwatch_button = ctk.CTkButton(self.stopwatch_frame, image=self.stopwatch_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
        self.stopwatch_button.grid(row=0, column=2, padx=1, pady=1, sticky="w")

    def update_time(self, time_label):
        self.stopwatch_label.config(text=time_label)
        
class Alarm:
    def __init__(self, parent, font_size):
        self.alarm_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.alarm_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.alarm_frame.grid_columnconfigure(1, weight=1)
        self.alarm_frame.grid_propagate(False)

        self.alarm_image = ctk.CTkImage(Image.open("./media/icons/alarm.png").resize((font_size, font_size)))

        self.alarm_label = ctk.CTkLabel(self.alarm_frame, text="00:00:00", font_size=font_size)
        self.alarm_label.grid(row=0, column=0, padx=1, pady=1)
        self.alarm_button = ctk.CTkButton(self.alarm_frame, image=self.alarm_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
        self.alarm_button.grid(row=0, column=2, padx=1, pady=1, sticky="w")

    def update_time(self, time_label):
        self.alarm_label.config(text=time_label)
        
class Doge:
    def __init__(self, parent, font_size):
        self.doge_frame = ctk.CTkFrame(parent, fg_color="black", corner_radius=0)
        self.doge_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.doge_frame.grid_columnconfigure(1, weight=1)
        self.doge_frame.grid_propagate(False)

        self.doge_image = ctk.CTkImage(Image.open("./media/icons/doge.png").resize((font_size, font_size)))

        self.doge_label = ctk.CTkLabel(self.doge_frame, text="00:00:00", font_size=font_size)
        self.doge_label.grid(row=0, column=0, padx=1, pady=1)
        self.doge_button = ctk.CTkButton(self.doge_frame, image=self.doge_image, text="", fg_color="black", hover_color="black", corner_radius=0, width=font_size, height=font_size)
        self.doge_button.grid(row=0, column=2, padx=1, pady=1, sticky="w")

    def update_time(self, time_label):
        self.doge_label.config(text=time_label)