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

def filter_and_process_data(file_path):
    """
    Read and process the CSV file for workshops filtering out waived payments.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1', sep=',')

        # Filter out rows where the 'Payment Source' is not 'Waived'
        df = df[df['Payment Source'] != 'Waived']

        # Filter dataframes for each workshop type
        CAWKSP = df[((df['Workshop Name'] == 'Child Abuse Workshop') | (df['Workshop Name'] == 'Child Abuse Workshop (New Program)'))]
        SAVE = df[df['Workshop Name'] == 'School Violence Prevention Workshop']
        DASA = df[df['Workshop Name'] == 'Dignity for All Students Act (DASA)']
        AUTISM = df[df['Workshop Name'] == 'AUTISM Workshop']
        SUBT = df[df['Workshop Name'] == 'Sub Teacher Online Training']
        SUBP = df[df['Workshop Name'] == 'Sub Paraprofessional Online Training']

        # Store filtered dataframes in a dictionary
        ws_dict = {'CAWKSP': CAWKSP, 'SAVE': SAVE, 'DASA': DASA, 'AUTISM': AUTISM, 'SUBT': SUBT, 'SUBP': SUBP}

        return ws_dict
    except Exception as e:
        raise ValueError("Error processing data:", e)

def plot_number_of_workshops(ws_dict):
    """
    Plot the number of each workshop completed by date
    """
    try:
        # Convert 'Status Last Updated On' column to datetime format for each dataframe and count the number of workshop for each date and sort by date
        sorted_dict = {}
        for key, value in ws_dict.items():
            if not value.empty:
                value['Status Last Updated On'] = pd.to_datetime(value['Status Last Updated On'], format='%m/%d/%y')
                sorted_dict[key] = value['Status Last Updated On'].value_counts().sort_index()
                print(sorted_dict[key])

        # Create the plot
        plt.figure(figsize=(10, 6))  # Adjust figure size

        colors = plt.cm.tab10.colors  # Get a list of colors from the 'tab10' colormap

        for i, (key, value) in enumerate(sorted_dict.items()):  # Iterate over sorted_dict and enumerate to get both index and value
            ax = value.plot(style='-', color=colors[i], label=key)  # Use the color from colors list and label with key

        ax.set_ylabel('Number Completed')
        ax.set_xlabel('Date')
        ax.set_title('Workshops Completed by Date')
        ax.grid(color='gray', linestyle='dashed')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()  # Adjust layout to prevent overlap
        plt.legend()  # Add legend
        plt.show()
    except Exception as e:
        raise ValueError("Error plotting workshops:", e)

def main():
    try:
        file_path = select_file()
        if not file_path:
            print("No file selected. Exiting...")
            return
        ws_dict = filter_and_process_data(file_path)
        if not ws_dict:
            print("No workshops found in the data.")
            return
        plot_number_of_workshops(ws_dict)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
