import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename

def select_file():
    """
    Function to select a file using Tkinter file dialog.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = askopenfilename()
    root.destroy()
    return file_path

def read_and_process_data(file_path, school_year):
    """
    Read and process the CSV file for a specific school year.
    """
    # Read the CSV file
    df = pd.read_csv(file_path, encoding='latin1', sep=',')
    
    # Filter the data to include only finalized staff and completed Last Notification Dates
    df = df[(df['Finalized on Payroll?'] == 'Y') & (df['Last Notification Date'] != 'Not Complete')]
    
    # Convert 'Last Notification Date' column to datetime format
    df['Last Notification Date'] = pd.to_datetime(df['Last Notification Date'], format = 'mixed')
    
    # Filter data for the specified school year
    start_date = f'{school_year}-09-01'  # Start of the school year
    end_date = f'{school_year + 1}-06-30'  # End of the school year
    df = df[(df['Last Notification Date'] > start_date) & (df['Last Notification Date'] < end_date)]
    return df

def plot_number_of_hires(df, school_year):
    """
    Plot the number of hires over time.
    """
    # Count the number of hires for each date and sort by date
    ts = df['Last Notification Date'].value_counts().sort_index()
    
    # Create the plot
    plt.figure(figsize=(10, 6))  # Adjust figure size
    ax = ts.plot(style = 'o-', color = 'b')  # Customize plot
    ax.set_ylabel('Number of Hires')
    ax.set_xlabel('Date')
    ax.set_title(f'SPA New Hires in {school_year}')
    ax.grid(color='gray', linestyle='dashed')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()
    return ts

def get_school_year():
    """
    Get the school year from user input.
    """
    school_year = None

    def submit():
        nonlocal school_year
        try:
            school_year = int(school_year_entry.get())
            root.destroy()  # Close the Tkinter window
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input! Please enter a valid school year.")

    root = tk.Tk()
    root.title("Enter School Year")

    school_year_label = tk.Label(root, text="School Year:")
    school_year_label.grid(row=0, column=0)
    school_year_entry = tk.Entry(root)
    school_year_entry.grid(row=0, column=1)

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=1, columnspan=2)

    root.mainloop()

    return school_year

def main():
    file_path = select_file()
    if not file_path:
        print("No file selected. Exiting...")
        return
    try:
        school_year = get_school_year()
        if school_year is None:
            print("No school year provided. Exiting...")
            return
        df = read_and_process_data(file_path, school_year)
        ts = plot_number_of_hires(df, school_year)
        print(ts)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
