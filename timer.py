import tkinter as tk
from tkinter import messagebox
import time
import threading
import pygame

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer")
        self.root.geometry("300x300")
        self.root.attributes('-topmost', 1)

        self.minutes = tk.StringVar(value="00")  # Set default value to "00"
        self.seconds = tk.StringVar(value="00")  # Set default value to "00"
        self.always_on_top = tk.BooleanVar(value=True)
        self.auto_restart = tk.BooleanVar(value=False)  # Checkbox variable for auto restart
        self.original_minutes = None
        self.original_seconds = None
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.paused = False
        self.remaining_time = 0

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Minutes:").pack()
        tk.Spinbox(self.root, from_=0, to=59, textvariable=self.minutes, format="%02.0f").pack()  # Spinbox for minutes
        tk.Label(self.root, text="Seconds:").pack()
        tk.Spinbox(self.root, from_=0, to=59, textvariable=self.seconds, format="%02.0f").pack()  # Spinbox for seconds

        tk.Checkbutton(self.root, text="Auto Restart with Previous Values", variable=self.auto_restart).pack()  # Checkbox for auto restart

        button_width = 20  # Width for buttons

        tk.Button(self.root, text="Start Timer", command=self.start_timer, width=button_width).pack(pady=2)
        tk.Button(self.root, text="Pause Timer", command=self.pause_timer, width=button_width).pack(pady=2)
        tk.Button(self.root, text="Reset Timer", command=self.reset_timer, width=button_width).pack(pady=2)
        tk.Button(self.root, text="Restart Timer", command=self.restart_timer, width=button_width).pack(pady=2)
        tk.Button(self.root, text="Stop Timer", command=self.stop_timer_and_reset, width=button_width).pack(pady=2)  # Stop Timer button
        tk.Checkbutton(self.root, text="Always on top", variable=self.always_on_top, command=self.toggle_always_on_top).pack(pady=2)

    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())

    def start_timer(self):
        if self.paused:
            self.paused = False
            self.stop_event.clear()
            self.timer_thread = threading.Thread(target=self.run_timer, args=(self.remaining_time,), daemon=True)
            self.timer_thread.start()
            return

        try:
            total_seconds = int(self.minutes.get()) * 60 + int(self.seconds.get())
            if total_seconds <= 0:
                raise ValueError("Time must be greater than zero.")
            self.original_minutes = self.minutes.get()
            self.original_seconds = self.seconds.get()
            if self.timer_thread and self.timer_thread.is_alive():
                self.stop_timer()
            self.stop_event.clear()
            self.timer_thread = threading.Thread(target=self.run_timer, args=(total_seconds,), daemon=True)
            self.timer_thread.start()
        except ValueError as e:
            messagebox.showerror("Invalid input", "Please enter valid numbers for minutes and seconds.")

    def pause_timer(self):
        self.paused = True
        self.stop_timer()

    def reset_timer(self):
        self.stop_timer()
        self.minutes.set(self.original_minutes)
        self.seconds.set(self.original_seconds)

    def stop_timer_and_reset(self):
        self.stop_timer()
        self.update_time(0, 0)  # Reset the timer values to 0

    def restart_timer(self):
        self.stop_timer()  # Stop the current timer
        if self.original_minutes is not None and self.original_seconds is not None:
            self.minutes.set(self.original_minutes)
            self.seconds.set(self.original_seconds)
        else:
            messagebox.showerror("Error", "No previous timer to restart.")
        
        self.start_timer()  # Start the timer

    def stop_timer(self):
        if self.timer_thread and self.timer_thread.is_alive():
            self.stop_event.set()
            self.timer_thread.join()

    def run_timer(self, total_seconds):
        while total_seconds > 0 and not self.stop_event.is_set():
            minutes, seconds = divmod(total_seconds, 60)
            self.update_time(minutes, seconds)
            time.sleep(1)
            total_seconds -= 1

        if not self.stop_event.is_set():
            self.update_time(0, 0)
            self.play_sound()

            if self.auto_restart.get():  # Check if auto restart is enabled
                self.restart_timer()
            else:
                messagebox.showinfo("Timer Done", "Time's up!")

    def update_time(self, minutes, seconds):
        self.remaining_time = minutes * 60 + seconds
        # Use `after` to update UI elements from the main thread
        self.root.after(0, lambda: self.minutes.set(f"{minutes:02}"))
        self.root.after(0, lambda: self.seconds.set(f"{seconds:02}"))

    def play_sound(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("sound/alert.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play sound: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()