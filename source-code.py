import tkinter as tk
from tkinter import messagebox
import random
import pandas as pd
from datetime import datetime, timedelta
import winsound
import openpyxl


class CountdownDialog(tk.Toplevel):
    #A custom countdown dialog window that inherits from tk.Toplevel. This class is used to display a countdown timer to the user.
    #Attributes:
       # label_text (tk.StringVar): A Tkinter StringVar object to dynamically update the label text.
       # label (tk.Label): A label widget to display the countdown message.
      #  ok_button (tk.Button): A button widget that allows the user to close the dialog once the countdown is complete.

    #Methods:
        #__init__(self, parent, duration): Constructor for the CountdownDialog. Initializes the dialog's UI components and starts the countdown.
          #  Args:
               # parent (tk.Widget): The parent widget.
             #   duration (int): The countdown duration in seconds.

     #   countdown(self): A method to handle the countdown logic. Updates the label text with the remaining time and enables the 'OK' button when the countdown reaches zero.
    
    def __init__(self, parent, duration):
        super().__init__(parent)
        self.title("Progress")
        self.duration = duration
        
        self.label_text = tk.StringVar()
        self.label_text.set(f"Please wait for {self.duration} seconds to start.")
        self.label = tk.Label(self, textvariable=self.label_text)
        self.label.pack(pady=20)
        
        self.ok_button = tk.Button(self, text="OK", state=tk.DISABLED, command=self.destroy)
        self.ok_button.pack(pady=20)
        
        self.countdown()

    def countdown(self):
        if self.duration > 0:
            minutes, seconds = divmod(self.duration, 60)
            self.label_text.set(f"You have completed the current phase! Please wait for {minutes} minutes and {seconds} seconds to continue.")
            self.duration -= 1
            self.after(1000, self.countdown)
        else:
            self.ok_button.config(state=tk.NORMAL)

class ChoiceExperiment(tk.Tk):

       
    #Initializes the ChoiceExperiment application window with necessary variables and UI elements.

   # Attributes:
      #  conditions (list): A list of dictionaries, each representing an experimental condition with specified probability and amount.
    #    current_condition_index (int): Index to track the current condition of the experiment.
       # trials_count (int): Counter for the number of trials conducted.
       # choice_count (dict): Dictionary to count the number of times options 'A' and 'B' are chosen.
      #  score (int): Variable to track the score of the participant.
       # start_time (datetime): Timestamp marking the start of the experiment.
        #data (list): List to store data about each trial.
        #proportions_b (list): List to track the proportion of choosing option 'B' in the last few trials.
        #elapsed_time_var (tk.StringVar): StringVar to dynamically update the elapsed time in the UI.
        #score_var (tk.StringVar): StringVar to dynamically update the score in the UI.
        #condition_start_time (datetime): Timestamp marking the start of the current condition.

    #This method also sets up the main window's title, size, and initializes the UI components like buttons and labels.
    
    def __init__(self):
        super().__init__()

        # Experimental Conditions
        self.conditions = [
            {"probability": 50, "amount": 100},
            {"probability": 75, "amount": 67},
            {"probability": 25, "amount": 200},
            {"probability": 10, "amount": 500},
            {"probability": 100, "amount": 100},
        ]
        
        self.current_condition_index = 0
        self.trials_count = 0
        self.choice_count = {'A': 0, 'B': 0}
        self.score = 0
        self.start_time = datetime.now()
        self.data = []
        self.proportions_b = []
        
        self.title("Choice Experiment")
        self.geometry("400x300")
        
        self.elapsed_time_var = tk.StringVar()
        self.elapsed_time_var.set("Elapsed time: 00:00")
        self.elapsed_time_label = tk.Label(self, textvariable=self.elapsed_time_var, font=("Arial", 16))
        self.elapsed_time_label.pack()
        
        self.score_var = tk.StringVar()
        self.score_var.set(f"Score: {self.score}")
        self.score_label = tk.Label(self, textvariable=self.score_var, font=("Arial", 16))
        self.score_label.pack()
        self.condition_start_time = datetime.now()

        self.create_buttons()
        self.update_elapsed_time()
        self.waiting = False

    def create_buttons(self):
        # Creates and arranges the choice buttons (A and B) on the application window.

    #This method first checks if the buttons already exist and destroys them to create new ones for the current condition. It then shuffles the positions (left and right) for the buttons to avoid positional bias.

   # Button A:
      #  - Fixed to offer a 100% chance of gaining 50 points immediately.
      #  - When clicked, it calls the 'choose_a' method.

    #Button B:
       # - The text and functionality of Button B are set by the 'set_option_b_text' method.
       # - Its attributes like probability, amount, and delay are based on the current condition.

   # The method ensures that each new trial presents the buttons afresh, thus maintaining the randomness and fairness of the choice presentation.
    
        if hasattr(self, 'btn_a'): self.btn_a.destroy()
        if hasattr(self, 'btn_b'): self.btn_b.destroy()
        
        positions = ['left', 'right']
        random.shuffle(positions)
        
        self.btn_a = tk.Button(self, command=self.choose_a, text="100% chance of 50 points\nImmediately")
        self.btn_a.pack(side=positions.pop(), padx=10)
        
        self.set_option_b_text()
        self.btn_b.pack(side=positions.pop(), padx=10)
        
    def set_option_b_text(self):
    # Configures the text and command of Button B based on the current experimental condition and a randomly chosen delay.

    # Retrieves the current condition from the 'conditions' list using 'current_condition_index'.
    # Randomly selects a delay (0, 3, or 6 seconds) that will be applied to Button B.

    # Creates Button B with:
    # - A command bound to the 'choose_b' method, passing the selected delay as an argument.
    # - Text displaying the probability and amount of points that can be won, along with the chosen delay.
    # This setup ensures that Button B's configuration is unique for each trial, making the experiment dynamic and engaging.

           
 
        condition = self.conditions[self.current_condition_index]
        delay = random.choice([0, 3, 6])
        self.btn_b = tk.Button(self, command=lambda: self.choose_b(delay), 
                            text=f"{condition['probability']}% chance of {condition['amount']} points\nAfter {delay} seconds")

    def choose_a(self):
    # Handles the event when Button A is chosen by the participant.

    # Retrieves the current experimental condition to determine the attributes for option B.
    # Randomly selects a delay for option B, which is used for recording the choice.

    # Records the participant's choice of option A with:
    # - 'A' as the chosen option.
    # - Zero delay since option A gives immediate reward.
    # - 100% probability and 50 points as the reward for option A.
    # - The attributes of option B (delay, probability, and amount) are recorded for comparison.

    # Refreshes the buttons for the next trial by calling 'create_buttons'.
    # Plays a sound to indicate the increment in points.

        condition = self.conditions[self.current_condition_index]
        delay_b = random.choice([0, 3, 6])
        self.record_choice('A', 0, 100, 50, 'B', delay_b, condition['probability'], condition['amount'])
        self.create_buttons()
        winsound.PlaySound('increment.wav', winsound.SND_FILENAME)
        
    def choose_b(self, delay):
    # Handles the event when Button B is chosen by the participant.

    # Retrieves the current experimental condition to determine the probability and amount associated with option B.

    # Disables both Button A and Button B to prevent further choices during the delay period.

    # Schedules a callback to the 'after_delay' method after the specified delay time.
    # The delay is converted to milliseconds (delay * 1000).
    # Passes the choice ('B'), delay, and the current condition's probability and amount to 'after_delay'.

        condition = self.conditions[self.current_condition_index]
        self.btn_a.config(state=tk.DISABLED)
        self.btn_b.config(state=tk.DISABLED)
        
        self.after(delay * 1000, self.after_delay, 'B', delay, condition['probability'], condition['amount'])
        
    def after_delay(self, choice, delay, probability, amount):
    # Called after the delay associated with choosing option B.

    # Re-enables both Button A and Button B to allow further choices.

    # Determines the reward for option B based on the specified probability.
    # If a random number from 1 to 100 is less than or equal to the probability, the participant wins the amount; otherwise, they win 0.

    # Records the participant's choice along with the outcome (won amount).
    # Parameters include choice details (option B), the delay, probability, amount won, and corresponding details of the not chosen option (option A).

    # Refreshes the buttons for the next trial by calling 'create_buttons'.

    # Plays a sound indicating the outcome: a positive sound if the participant wins something (amount > 0), otherwise a null sound.

        self.btn_a.config(state=tk.NORMAL)
        self.btn_b.config(state=tk.NORMAL)
        
        condition = self.conditions[self.current_condition_index]
        won_amount = amount if random.randint(1, 100) <= probability else 0
        self.record_choice(choice, delay, probability, won_amount, 'A', 0, 100, 50)
        self.create_buttons()
        
        if won_amount > 0:
            winsound.PlaySound('increment.wav', winsound.SND_FILENAME)
        else:
            winsound.PlaySound('null.wav', winsound.SND_FILENAME)

        
    def record_choice(self, chosen, delay_chosen, prob_chosen, amount_chosen, not_chosen, delay_not_chosen, prob_not_chosen, amount_not_chosen):
    # Records the participant's choice and its details for each trial.

    # Increments the total number of trials.
    # Increments the count for the chosen option (either 'A' or 'B').

    # Updates the participant's score based on the amount won in the chosen option.
    # Updates the score display in the application's UI.

    # Appends a record to the 'data' list with the following details:
    # - Timestamp of the choice.
    # - Chosen option and its details (delay, probability, amount).
    # - Not chosen option and its details.
    # - Current score after making the choice.

    # Every 10 trials, evaluates the condition to check for a response pattern and potentially move to the next condition.

        self.trials_count += 1
        self.choice_count[chosen] += 1
        self.score += amount_chosen
        self.score_var.set(f"Score: {self.score}")
        
        self.data.append({
            'timestamp': datetime.now(),
            'chosen_option': chosen,
            'chosen_delay': delay_chosen,
            'chosen_probability': prob_chosen,
            'chosen_amount': amount_chosen,
            'not_chosen_option': not_chosen,
            'not_chosen_delay': delay_not_chosen,
            'not_chosen_probability': prob_not_chosen,
            'not_chosen_amount': amount_not_chosen,
            'score': self.score
        })
        
        if self.trials_count % 10 == 0:
            self.evaluate_condition()
            
                                           
    def evaluate_condition(self):
    # Evaluates the participant's response pattern after every 10 trials to determine if it's time to move to the next condition.

    # Calculates the proportion of choosing option B in the last 10 trials and appends it to the 'proportions_b' list.

    # If there are at least 3 proportions recorded:
    # - Determines the average of the last three proportions.
    # - Checks if the participant's choices have stabilized (i.e., the absolute difference from the average is less than or equal to 0.1 for each of the last three proportions).
    
    # If the response pattern has stabilized:
    # - Advances to the next condition by incrementing 'current_condition_index'.

    # For the transition to the next condition:
    # - Calculates elapsed time and remaining time before the next condition starts.
    # - Disables both choice buttons and displays a countdown dialog with the remaining time.
    # - Waits until the countdown finishes before re-enabling the buttons and resetting the condition start time.
    # - If all conditions are completed, ends the experiment.

    # Resets the trials count and choice counts, and refreshes the buttons for the new condition.

        proportion_b = self.choice_count['B'] / 10
        self.proportions_b.append(proportion_b)
        
        if len(self.proportions_b) >= 3:
            last_three_proportions = self.proportions_b[-3:]
            avg_proportion = sum(last_three_proportions) / 3
            if all(abs(proportion - avg_proportion) <= 0.1 for proportion in last_three_proportions):
                self.current_condition_index += 1

                # Show the notification when the phase progresses with the remaining time
                if self.current_condition_index < len(self.conditions):
                    # Calculate the elapsed and remaining time immediately before creating the dialog
                    elapsed_time = datetime.now() - self.condition_start_time
                    remaining_time = timedelta(minutes=5) - elapsed_time
                    seconds_remaining = remaining_time.seconds
                    
                    # Disable buttons
                    self.btn_a.config(state=tk.DISABLED)
                    self.btn_b.config(state=tk.DISABLED)
                    self.waiting = True
                    
                    # Show the custom dialog
                    dialog = CountdownDialog(self, seconds_remaining)
                    self.wait_window(dialog)
                    
                    # Once the dialog is closed, end the waiting period and then reset the condition_start_time
                    self.end_waiting()
                    self.condition_start_time = datetime.now()
                else:
                    self.end_experiment()
                    return

                self.proportions_b = []

        self.trials_count = 0
        self.choice_count = {'A': 0, 'B': 0}
        self.create_buttons()

    def end_waiting(self):
    # Re-enables the choice buttons (A and B) and ends the waiting period.

    # Configures Button A and Button B to be active (clickable) again, allowing the participant to continue making choices.
    # Sets the 'waiting' flag to False, indicating that the countdown period is over and the experiment can proceed.

        self.btn_a.config(state=tk.NORMAL)
        self.btn_b.config(state=tk.NORMAL)
        self.waiting = False

    def check_condition_duration(self):
    # Checks if the current condition's duration has exceeded a predefined limit (5 minutes) and if the application is not already in a waiting state.

    # Calculates the elapsed time since the start of the current condition.

    # If the elapsed time is equal to or greater than 5 minutes and the application is not in a waiting state:
    # - Proceeds to the next condition by incrementing 'current_condition_index'.

    # For the transition to the next condition:
    # - If there are more conditions to go through, calculates the full 5 minutes as the remaining time and shows a countdown dialog.
    # - Disables both choice buttons to prevent further interactions during the countdown.
    # - Sets the 'waiting' flag to True, indicating an ongoing waiting period.

    # After the countdown dialog is closed:
    # - Calls 'end_waiting' to re-enable the buttons and reset the 'waiting' flag.
    # - Resets the start time for the new condition.

    # If all conditions have been completed, calls 'end_experiment' to finish the experiment.

    # Resets the trial count, choice counts, and refreshes the buttons for the new condition.

        elapsed_time = datetime.now() - self.condition_start_time
        if elapsed_time >= timedelta(minutes=5) and not self.waiting:
            # Proceed to next condition
            self.current_condition_index += 1

            if self.current_condition_index < len(self.conditions):
                # Calculate the elapsed and remaining time immediately before creating the dialog
                elapsed_time = datetime.now() - self.condition_start_time
                remaining_time = timedelta(minutes=5) - elapsed_time
                seconds_remaining = 5 * 60  # This is a full 5 minutes
                
                # Disable buttons
                self.btn_a.config(state=tk.DISABLED)
                self.btn_b.config(state=tk.DISABLED)
                self.waiting = True
                
                # Show the custom dialog
                dialog = CountdownDialog(self, seconds_remaining)
                self.wait_window(dialog)
                
                # Once the dialog is closed, end the waiting period and then reset the condition_start_time
                self.end_waiting()
                self.condition_start_time = datetime.now()
            else:
                self.end_experiment()

            self.proportions_b = []
            self.trials_count = 0
            self.choice_count = {'A': 0, 'B': 0}
            self.create_buttons()

            
    def end_experiment(self):
    # Finalizes the experiment and handles data saving and UI closure.

    # Disables both choice buttons (A and B) to prevent further interactions.

    # Converts the collected data into a pandas DataFrame and saves it to an Excel file.
    # The filename is timestamped to ensure uniqueness.

    # Opens the saved Excel file using openpyxl for further processing.
    # Adjusts the width of each column in the Excel sheet based on the maximum length of the data in each column for better readability.

    # Saves the adjusted Excel file.

    # Prints a message to the console indicating the end of the experiment and the filename where results are saved.

    # Shows a thank you message to the participant using a message box.

    # Destroys the application window, effectively ending the application.

        self.btn_a.config(state=tk.DISABLED)
        self.btn_b.config(state=tk.DISABLED)
        
        df = pd.DataFrame(self.data)
        filename = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        
        workbook = openpyxl.load_workbook(filename)
        worksheet = workbook.active
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try: 
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        workbook.save(filename)
        
        print(f"Experiment ended. Results saved to {filename}.")
        
        messagebox.showinfo("Thank you!", "Thank you for participating.")
        self.destroy()
        
    def update_elapsed_time(self):
    # Continuously updates the elapsed time in the application's UI.

    # Calculates the elapsed time since the start of the experiment.
    # Converts the elapsed time into minutes and seconds format.

    # Updates the 'elapsed_time_var' StringVar, which in turn updates the elapsed time label in the UI.

    # Calls itself after a delay of 1000 milliseconds (1 second), creating a loop to update the time every second.

    # Also calls 'check_condition_duration' to regularly check if the current condition's duration has been met, facilitating timely transition to the next condition.

        elapsed_time = datetime.now() - self.start_time
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        self.elapsed_time_var.set(f"Elapsed time: {minutes:02}:{seconds:02}")
        
        self.after(1000, self.update_elapsed_time)
        self.check_condition_duration()
if __name__ == "__main__":
    app = ChoiceExperiment()
    app.mainloop()
