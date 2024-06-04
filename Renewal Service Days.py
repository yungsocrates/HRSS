import pandas as pd  # Import Pandas library for data manipulation
import tkinter as tk  # Import Tkinter for GUI operations
from tkinter.filedialog import askopenfilename, asksaveasfilename  # Import file dialog functions

def select_file():
    """
    Function to select a file using Tkinter file dialog.
    """
    root = tk.Tk()  # Create a Tkinter root window
    root.withdraw()  # Hide the root window
    file_path = askopenfilename()  # Open file dialog and get file path
    root.destroy()  # Destroy the root window
    return file_path  # Return the selected file path

def choose_title():
    """
    Function to choose between two different options using a checkbox.
    """
    root = tk.Tk()  # Create a Tkinter root window
    root.withdraw()  # Hide the root window
    
    # Create a new window for the options
    option_window = tk.Toplevel(root)
    
    # Create a label to explain the purpose
    label = tk.Label(option_window, text="Please choose the sub title:")
    label.pack()
    
    # Create a variable to hold the choice
    choice_var = tk.IntVar()
    
    # Create checkboxes for the options
    option1_checkbox = tk.Checkbutton(option_window, text="Sub Teachers", variable=choice_var, onvalue=1, offvalue=0)
    option1_checkbox.pack()
    
    option2_checkbox = tk.Checkbutton(option_window, text="Sub Paras", variable=choice_var, onvalue=2, offvalue=0)
    option2_checkbox.pack()
    
    # Create a button to confirm the choice
    confirm_button = tk.Button(option_window, text="Confirm", command=lambda: root.quit())
    confirm_button.pack()
    
    # Wait for the user to confirm the choice
    root.mainloop()
    
    # Get the chosen option
    choice = choice_var.get()
    
    # Destroy the options window
    option_window.destroy()
    
    root.destroy()  # Destroy the root window
    return choice  # Return the chosen option

def process_and_calculate_days(file_path, title):
    """
    Function to process the selected file and calculate days worked.
    """
    days_worked = dict()  # Dictionary to store days worked
    if title == 1:  # If title corresponds to "Sub Teachers"
        # Read CSV file skipping first, second, and fourth rows, selecting every other column, and specifying encoding
        df = pd.read_csv(file_path, skiprows=[0, 1, 3], usecols=[2*i for i in range(0, 19)], encoding='UTF-8', sep=',')
        for index, row in df.iterrows():
            # Calculate days worked for 'O' entries and update dictionary
            if row['C'] == 'O':
                if row['I'] not in days_worked:
                    days_worked[row['I']] = (row['HRS']*60 + row['MINS']) / 380
                else:
                    days_worked[row['I']] += (row['HRS']*60 + row['MINS']) / 380
        # Create DataFrame from dictionary and round days to two decimal places
        df_final = pd.DataFrame(days_worked.items(), columns=['EISID', 'DAYS']).round(2)
        df_final['EISID'] = df_final['EISID'].astype(str).str.zfill(7)  # Fill leading zeros in EISID
        return df_final
    
    elif title == 2:  # If title corresponds to "Sub Paras"
        # Read CSV file skipping first row, selecting every other column, and specifying encoding
        df = pd.read_csv(file_path, skiprows=[1], usecols=[2*i for i in range(0, 10)], encoding='UTF-8', sep=',')
        for index, row in df.iterrows():
            # Calculate days worked and update dictionary
            if row['EISID'] not in days_worked:
                days_worked[row['EISID']] = (row['HRS']*60 + row['MINS']) / 360
            else:
                days_worked[row['EISID']] += (row['HRS']*60 + row['MINS']) / 360
        # Create DataFrame from dictionary and round days to two decimal places
        df_final = pd.DataFrame(days_worked.items(), columns=['EISID', 'DAYS']).round(2)
        df_final['EISID'] = df_final['EISID'].astype(str).str.zfill(7)  # Fill leading zeros in EISID
        return df_final

def main():
    """
    Main function to orchestrate the workflow.
    """
    # Select a file using file dialog
    file_path = select_file()
    
    if not file_path:
        print("No file selected.")
        return
    
    title = choose_title()  # Choose title using checkbox dialog

    # Process the selected file and calculate days for each school year
    output_df = process_and_calculate_days(file_path, title)
    
    if not output_df.empty:
        # Print output DataFrame
        print('------------------------------------------------------------')
        print(output_df)
        print('------------------------------------------------------------')
        
        # Save output to a CSV file
        output_file = asksaveasfilename()
        if output_file:
            output_df.to_csv(output_file + '.csv', sep=',', index=False)
        else:
            print("No file selected for saving.")
    else:
        print("No data available.")

if __name__ == "__main__":
    main()
