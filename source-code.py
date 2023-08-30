import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import font
import winsound
import random
import matplotlib.pyplot as plt
import time
import numpy as np
import copy
import csv
from collections import defaultdict
import math
import json
import os
from tkinter import filedialog
import pandas as pd

class Phase:
    def __init__(self, duration, schedules):
        self.duration = duration
        self.schedules = schedules





class DrawingCanvas(tk.Canvas):
    def __init__(self, master, width, height, x, y):
        super().__init__(master, width=width, height=height, bg='white')  # Set background color to white
        self.pack()
        self.place(x=x, y=y)

        # Add a border to the drawing canvas and keep a reference to it
        self.border_rectangle = self.create_rectangle(0, 0, width, height, outline='black', width=2)

        # Lower the border rectangle to be behind other drawings
        self.tag_lower(self.border_rectangle)


        # Drawing related attributes
        self.drawing = False
        self.last_x = 0
        self.last_y = 0

        # Binding events
        self.bind("<Button-1>", self.start_drawing)
        self.bind("<B1-Motion>", self.draw)
        self.bind("<ButtonRelease-1>", self.stop_drawing)

    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        if self.drawing:
            self.create_line(self.last_x, self.last_y, event.x, event.y, fill="black")
            self.last_x = event.x
            self.last_y = event.y

    def stop_drawing(self, event):
        self.drawing = False

    def clear(self):
        self.delete("all")


class OperantExperiment:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Human Operant Research Program")
        self.root.attributes('-fullscreen', True)
        self.images = ["img1.png", "img2.png", "img3.png", "img4.png", "img5.png", "img6.png"]

        # Calculate canvas dimensions and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        canvas_width = screen_width
        canvas_height = screen_height // 5  # Canvas height is 1/5th of the screen height
        canvas_x = 0
        canvas_y = screen_height - canvas_height  # Bottom of the screen

        self.drawing_canvas = DrawingCanvas(self.root, canvas_width, canvas_height, canvas_x, canvas_y)

        # Add a border to the drawing canvas
        self.drawing_canvas.create_rectangle(0, 0, canvas_width, canvas_height, width=2)
        # Add label to the drawing canvas
        self.drawing_canvas.create_text(canvas_width//2, canvas_height//2, text="Draw here if Bored", font=("Arial", 16))

        self.image_canvas = tk.Canvas(self.root, width=800, height=600)
        self.image_canvas.pack()
        self.image_obj = None
        self.vi_delays = [0, 0, 0, 0]
        self.last_reinforcement_timestamps = [-99999 for _ in range(4)]  # Initialize with negative values
        self.phase_button_presses = defaultdict(lambda: defaultdict(int))
        self.points = 0
        self.button_presses = [0, 0, 0, 0]
        self.time_remaining = 0
        self.button_press_timestamps = [[] for _ in range(4)]
        self.last_reinforcement_timestamps = [0 for _ in range(4)]  # Add this line

        self.phases = []
        self.current_phase = 0
        self.fi_counters = [0, 0, 0, 0]
        self.vi_counters = [0, 0, 0, 0]



    def press_button(self, i):
        self.button_presses[i] += 1
        global_time = sum(phase.duration for phase in self.phases) - self.time_remaining
        self.button_press_timestamps[i].append(global_time)
        self.phase_button_presses[self.current_phase][i] += 1

        self.apply_reinforcement_schedule(i)

        self.points_label.config(text=f"Points: {self.points}")
    
    def reset_counters(self):
        self.button_presses = [0, 0, 0, 0]
        self.last_reinforcement_timestamps = [0 for _ in range(4)]
        self.vi_delays = [0, 0, 0, 0]
        self.fi_counters = [0, 0, 0, 0]
        self.vi_counters = [0, 0, 0, 0]
        self.drawing_canvas.clear()  # Clear the drawing canvas at the end of each phase
    def save_phases(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", 
                                                filetypes=[("JSON files", "*.json")],
                                                title="Choose filename to save phases")
        if filename:  # If a filename is provided (i.e., the dialog is not cancelled)
            with open(filename, 'w') as file:
                json.dump([phase.__dict__ for phase in self.phases], file)

    def load_phases(self):
        filename = filedialog.askopenfilename(defaultextension=".json", 
                                            filetypes=[("JSON files", "*.json")],
                                            title="Choose a file to load phases")
        if filename:  # If a filename is provided (i.e., the dialog is not cancelled)
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.phases = [Phase(d['duration'], d['schedules']) for d in data]
                print(f"Phases have been successfully loaded from {filename}.")
            else:
                print(f"No file named {filename} found.")


    
    def main(self):
        filename = input("Enter the filename of the phases data you want to load: ")
        self.load_phases(filename)
        self.start_menu()


    def start_menu(self):
        self.start_window = tk.Toplevel(self.root)
        self.start_window.title("Start Menu")
        self.start_window.geometry("300x250")

        self.start_window.focus_force()  # Force focus on the start window
        self.start_window.grab_set()  # Grab all events to start window
        self.root.iconify()  # Minimize the main root window

        set_phases_button = tk.Button(self.start_window, text="Set Phases", command=self.set_phases)
        set_phases_button.pack(pady=10)

        start_experiment_button = tk.Button(self.start_window, text="Start Experiment", command=self.start_experiment)
        start_experiment_button.pack(pady=10)
        
        load_phases_button = tk.Button(self.start_window, text="Load Phases", command=self.load_phases)
        load_phases_button.pack(pady=10)
        
        save_phases_button = tk.Button(self.start_window, text="Save Phases", command=self.save_phases)
        save_phases_button.pack(pady=10)

        self.start_window.protocol("WM_DELETE_WINDOW", self.root.destroy)  # Exit the program when start menu is closed

        self.root.deiconify()  # Un-minimize the main root window
        self.root.focus_force()  # Force focus on the main root window

        self.start_window.mainloop()




    def apply_reinforcement_schedule(self, i):
        schedule_type, schedule_value = self.phases[self.current_phase].schedules[i]

        if len(self.button_press_timestamps[i]) == 0:
            return

        global_time = sum(phase.duration for phase in self.phases) - self.time_remaining
        time_since_last_press = global_time - self.button_press_timestamps[i][-1]
        time_since_last_reinforcement = global_time - self.last_reinforcement_timestamps[i]

        if schedule_type == "FR" and self.button_presses[i] % schedule_value == 0:
            self.points += 1
            self.play_feedback("positive")
        elif schedule_type == "FI":
            if time_since_last_reinforcement >= schedule_value:
                self.points += 1
                self.play_feedback("positive")
                self.last_reinforcement_timestamps[i] = global_time
                    
        elif schedule_type == "VR":
            if random.random() < 1 / schedule_value:
                self.points += 1
                self.play_feedback("positive")
        elif schedule_type == "VI":
            if time_since_last_reinforcement >= self.vi_delays[i]:
                self.points += 1
                self.play_feedback("positive")
                self.last_reinforcement_timestamps[i] = global_time
                self.vi_delays[i] = random.uniform(schedule_value * 0.5, schedule_value * 1.5)  # Update the delay

        elif schedule_type == "RC":  
            if self.button_presses[i] % schedule_value == 0:
                self.points -= 1
                self.play_feedback("aversive")


    def set_phases(self):
        num_phases = simpledialog.askinteger("Phases", "Enter the number of phases (1-6):", minvalue=1, maxvalue=6)

        for i in range(num_phases):
            phase_duration = simpledialog.askinteger(f"Phase {i+1}", f"Enter the duration of phase {i+1} in seconds:")
            phase_schedules = []

            for j in range(4):
                schedule_type = simpledialog.askstring(f"Phase {i+1} Button {j+1}", f"Enter the schedule type for button {j+1} in phase {i+1} (FR, FI, VR, VI, RC, NCR):")  # Included "NCR" as an option
                schedule_value = simpledialog.askinteger(f"Phase {i+1} Button {j+1}", f"Enter the schedule value for button {j+1} in phase {i+1} (Negative integer for aversive):")
                # Only add the button if both the schedule type and value are not None
                if schedule_type is not None and schedule_value is not None:
                    phase_schedules.append((schedule_type, schedule_value))
                else:
                    phase_schedules.append((None, None))

            phase = Phase(phase_duration, copy.deepcopy(phase_schedules))  # Create a deep copy of the schedules
            self.phases.append(phase)


    def start_experiment(self):
        self.start_window.destroy()
        self.prepare_experiment()

    def prepare_experiment(self):
        total_duration = sum(phase.duration for phase in self.phases)
        self.time_remaining = total_duration
        self.schedules = self.phases[self.current_phase].schedules
        self.start_experiment_screen()


    def start_experiment_screen(self):
        self.points = 0
        self.button_presses = [0, 0, 0, 0]

        button_font = font.Font(size=14)
        button_colors = ["red", "blue", "green", "yellow"]
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.buttons = []
        for i, (schedule_type, schedule_value) in enumerate(self.schedules):
            if schedule_type is None or schedule_value is None:
                continue
            button = tk.Button(self.root, text="", command=lambda i=i: self.press_button(i),  # Removed button label here
                               font=button_font, bg=button_colors[i], fg="#ffffff", width=15, height=3)
            button.place(x=screen_width // (len(self.schedules)+1) * (i+1), y=screen_height // 2 - 50)
            self.buttons.append(button)

        self.timer_label = tk.Label(self.root, text=f"Time remaining: {self.time_remaining}s", font=font.Font(size=12), bg=self.root.cget('bg'))
        self.timer_label.place(x=screen_width // 2 - 100, y=screen_height // 2 + 50)

        self.points_label = tk.Label(self.root, text=f"Points: {self.points}", font=font.Font(size=20, weight="bold"), bg=self.root.cget('bg'))
        self.points_label.place(x=screen_width // 2 - 50, y=screen_height // 2 - 100)

        self.display_image(self.images[self.current_phase])  # Display the image corresponding to the current phase

        self.root.after(1000, self.update_timer)
        self.root.after(3000, self.move_buttons_loop)
        self.root.mainloop()


    def update_timer(self):
        self.time_remaining -= 1
        self.timer_label.config(text=f"Time remaining: {self.time_remaining}s")

        global_time = sum(phase.duration for phase in self.phases) - self.time_remaining

        # Checking for NCR reinforcement here
        for i, (schedule_type, schedule_value) in enumerate(self.phases[self.current_phase].schedules):
            if schedule_type == "NCR":
                time_since_last_reinforcement = global_time - self.last_reinforcement_timestamps[i]
                if time_since_last_reinforcement >= schedule_value:
                    self.points += 1
                    self.play_feedback("positive")
                    self.last_reinforcement_timestamps[i] = global_time

        if self.time_remaining <= 0:
            self.root.withdraw()
            self.display_results()
            self.root.destroy()
        else:
            if self.time_remaining <= sum(phase.duration for phase in self.phases[self.current_phase + 1:]):
                self.current_phase += 1
                self.schedules = self.phases[self.current_phase].schedules

                # Update the image displayed
                if self.current_phase < len(self.images):
                    self.display_image(self.images[self.current_phase])

                self.reset_counters()  # Reset counters at the end of each phase

            self.root.after(1000, self.update_timer)



    def display_image(self, image_filename):
        try:
            image = tk.PhotoImage(file=image_filename)
            if self.image_obj is None:
                self.image_obj = self.image_canvas.create_image(400, 300, image=image)
            else:
                self.image_canvas.itemconfig(self.image_obj, image=image)
            self.image_canvas.image = image
        except tk.TclError:
            print(f"No image file named {image_filename} found. Continuing without an image.")



    def play_feedback(self, feedback_type):
        if feedback_type == "positive":
            winsound.PlaySound('positive.wav', winsound.SND_ASYNC)
            self.root.config(bg="green")
        elif feedback_type == "aversive":
            winsound.PlaySound('aversive.wav', winsound.SND_ASYNC)
            self.root.config(bg="red")

        self.root.after(200, lambda: self.root.config(bg="SystemButtonFace"))

    def move_buttons(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        button_width = 15 * 10  # assuming 1 character width is 10 pixels
        button_height = 3 * 25  # assuming 1 character height is 25 pixels

        for i, button in enumerate(self.buttons):
            x = random.randint(0, screen_width - button_width)
            y = random.randint(0, screen_height - button_height)
            button.place(x=x, y=y)

    def move_buttons_loop(self):
        self.move_buttons()
        self.root.after(3000, self.move_buttons_loop)


    def save_data(self):
        with open('experiment_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['button', 'button_press_timestamps']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(4):
                writer.writerow({
                    'button': i + 1,
                    'button_press_timestamps': self.button_press_timestamps[i],
                    
                })

    def display_results_table(self):
        buttons_to_display_str = simpledialog.askstring("Buttons to Display", "Enter the button numbers to display separated by commas (e.g., 1,2,3):")
        buttons_to_display = [int(button.strip()) for button in buttons_to_display_str.split(',') if button.strip().isdigit()]

        # Initialize a list to hold the dictionaries for each button and phase
        results = []

        phase_start_time = 0
        for phase_num, phase in enumerate(self.phases, start=1):
            phase_end_time = phase_start_time + phase.duration

            for button in buttons_to_display:
                # If the button was not defined, continue
                if phase.schedules[button-1][0] is None:
                    continue

                # Calculate total responses and average rate of responding for this button in the phase
                total_responses = sum(1 for t in self.button_press_timestamps[button-1] if phase_start_time <= t < phase_end_time)
                average_rate = total_responses / phase.duration

                # Append this data as a dictionary to the results list
                results.append({
                    'Phase': phase_num,
                    'Button': button,
                    'Duration': phase.duration,
                    'Responses': total_responses,
                    'Avg. Rate': average_rate,
                })

            phase_start_time = phase_end_time

        # Convert results list to pandas DataFrame
        df = pd.DataFrame(results)

        # Rearrange columns order
        df = df[['Phase', 'Button', 'Duration', 'Responses', 'Avg. Rate']]

        # Save to Excel
        df.to_excel('results.xlsx', index=False)

        # Display the table
        print(df)




    def display_results(self):
        self.save_data()
        buttons_to_display_str = simpledialog.askstring("Buttons to Display", "Enter the button numbers to display separated by commas (e.g., 1,2,3):")
        buttons_to_display = [int(button.strip()) for button in buttons_to_display_str.split(',') if button.strip().isdigit()]

        total_duration = sum(phase.duration for phase in self.phases)

        # Cumulative record graph
        cumulative_button_presses = [[0] * (total_duration + 1) for _ in range(4)]

        for i in range(4):
            if self.phases[0].schedules[i][0] is None:  # Skip the button if it wasn't defined
                continue
            current_timestamp_index = 0
            for t in range(total_duration + 1):
                while current_timestamp_index < len(self.button_press_timestamps[i]) and self.button_press_timestamps[i][current_timestamp_index] <= t:
                    current_timestamp_index += 1
                cumulative_button_presses[i][t] = current_timestamp_index

        plt.figure()
        button_colors = ["red", "blue", "green", "yellow"]
        for i, button_press in enumerate(cumulative_button_presses):
            if self.phases[0].schedules[i][0] is not None:  # Only plot the button if it was defined
                plt.plot(list(range(total_duration + 1)), button_press, label=f"Button {i+1}", color=button_colors[i])

        plt.xlabel('Time (s)')
        plt.ylabel('Cumulative Button Presses')
        plt.title('Cumulative Record of Responses')
        plt.legend()

        # Rate of responding graph
        data_points_per_unit_time = 1 / 5.0  # one data point every 5 seconds

        plt.figure()
        markers = ['o', 's', '^', 'v']
        lines = ['-', '--', '-.', ':']

        phase_change_timestamps = [0] + [phase.duration for phase in self.phases]
        for t in range(1, len(phase_change_timestamps)):
            phase_change_timestamps[t] += phase_change_timestamps[t - 1]

        for i in range(4):
            if i + 1 in buttons_to_display:
                for t in range(len(phase_change_timestamps) - 1):
                    start = phase_change_timestamps[t]
                    end = phase_change_timestamps[t + 1]
                    data_points_this_phase = int((end - start) * data_points_per_unit_time)
                    interval_size = (end - start) / data_points_this_phase  # Float division

                    responding_rates = []
                    for j in range(data_points_this_phase):
                        interval_start = math.floor(start + j * interval_size)  # Round down
                        interval_end = math.ceil(interval_start + interval_size)  # Round up
                        responding_rate = (cumulative_button_presses[i][interval_end] - cumulative_button_presses[i][interval_start]) / interval_size
                        responding_rates.append(responding_rate)

                    x_values = [start + j * interval_size + interval_size / 2 for j in range(data_points_this_phase)]
                    plt.plot(x_values, responding_rates, marker=markers[i], markersize=5, linestyle=lines[i], color='black')

        # Draw vertical lines for phase changes
        for t in range(1, len(phase_change_timestamps) - 1):
            plt.axvline(x=phase_change_timestamps[t], color='black', linestyle='-', linewidth=1)

        plt.xlabel('Time (s)')
        plt.ylabel('Rate')
        plt.title('Rate of Responding')

        custom_lines = [plt.Line2D([0], [0], color='black', lw=1, linestyle=linestyle) for linestyle in lines]
        plt.legend(custom_lines, [f"Button {button}" for button in buttons_to_display])

        plt.show()

        # Display results table
        self.display_results_table()







if __name__ == "__main__":
    experiment = OperantExperiment()
    experiment.start_menu()
    experiment.main()
