import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def select_file():
    """
    Function to select a file using Tkinter file dialog.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = askopenfilename()
    root.destroy()
    return file_path

def process_and_calculate_hours(file_path, start_year, end_year):
    """
    Function to process the data and calculate hours for each school year.
    """
    # Read file data into pandas dataframe
    df = pd.read_csv(file_path, names=['1', '2', '3', 'EIS ID', 'EMPL ID', 'SSN', 'PR LST N', 'PR FIR N',
                                       'SVC DATE', 'LOC', 'TITLE', 'JOB', 'SVC HRS', 'SVC MINS'], skiprows=21,
                     usecols=[i for i in range(3, 14)], sep='\s+')
    
    # Convert NAs to 0 and floats to ints
    df[['EIS ID', 'EMPL ID', 'SVC HRS', 'SVC MINS']] = df[['EIS ID', 'EMPL ID', 'SVC HRS', 'SVC MINS']].fillna(
        0).astype(int)
    
    # Separate data by school year
    SY_dict = {}
    for year in range(start_year, end_year):
        SY_dict[year] = df[(df['SVC DATE'] > f'{year}-09-01') & (df['SVC DATE'] < f'{year + 1}-06-30')]
    
    output_dfs = []
    for year, school_year in SY_dict.items():
        if not school_year.empty:
            # Calculate total hours and average hours per week
            svc_hrs_sum = school_year['SVC HRS'].sum()
            svc_mins_sum = school_year['SVC MINS'].sum()
            total_hrs = svc_hrs_sum + svc_mins_sum / 60
            avg_hrs_per_week = total_hrs / 26

            # Round to one decimal point
            total_hrs = round(total_hrs, 1)
            avg_hrs_per_week = round(avg_hrs_per_week, 1)
            
            # Create DataFrame for output
            output_data = pd.DataFrame({'School Year': [year], 'Total Hours Worked': [total_hrs],
                                        'Average Hours Per Week': [avg_hrs_per_week]})
            output_dfs.append(output_data)

    return output_dfs

def get_start_end_years():
    """
    Function to get start and end years from the user.
    """
    start_year, end_year = None, None

    def submit():
        nonlocal start_year, end_year
        start_year = int(start_year_entry.get())
        end_year = int(end_year_entry.get())
        root.destroy()  # Close the Tkinter window

    root = tk.Tk()
    root.title("Enter Start and End Years")

    start_year_label = tk.Label(root, text="Start Year:")
    start_year_label.grid(row=0, column=0)
    start_year_entry = tk.Entry(root)
    start_year_entry.grid(row=0, column=1)

    end_year_label = tk.Label(root, text="End Year:")
    end_year_label.grid(row=1, column=0)
    end_year_entry = tk.Entry(root)
    end_year_entry.grid(row=1, column=1)

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=2, columnspan=2)

    root.mainloop()

    return start_year, end_year

def display_output(output_df):
    """
    Function to display the output in a Tkinter window.
    """
    root = tk.Tk()
    root.title("Output")
    
    table = tk.Text(root, height=10, width=75)
    table.grid(row=0, column=0, padx=25, pady=25)

    # Insert the output DataFrame into the Text widget
    table.insert(tk.END, output_df)
    
    root.mainloop()

def main():
    """
    Main function to orchestrate the workflow.
    """
    # Get start and end years from user
    start_year, end_year = get_start_end_years()
    
    # Select a file using file dialog
    file_path = select_file()
    
    if not file_path:
        print("No file selected.")
        return
    
    # Process the selected file and calculate hours for each school year
    output_dfs = process_and_calculate_hours(file_path, start_year=start_year, end_year=end_year)
    
    if output_dfs:
        # Concatenate output DataFrames
        output_df = pd.concat(output_dfs, ignore_index=True)
        print('------------------------------------------------------------')
        print(output_df)
        print('------------------------------------------------------------')
        
        # save output to a CSV file
        output_file = asksaveasfilename()
        if output_file:
            output_df.to_csv(output_file + '.csv', sep=',', index=False)
        else:
            print("No file selected for saving.")
        
        # Display the output in a Tkinter window
        display_output(output_df)
    else:
        print("No data available.")

if __name__ == "__main__":
    main()
