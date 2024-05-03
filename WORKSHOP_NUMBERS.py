import pandas as pd
import tkinter as tk
import numpy as np
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

def filter_and_process_workshop_data(file_path):
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
        AUTISM = df[df['Workshop Name'] == 'Autism Workshop']
        SUBT = df[df['Workshop Name'] == 'Sub Teacher Online Training']
        SUBP = df[df['Workshop Name'] == 'Sub Paraprofessional Online Training']

        # Store filtered dataframes in a dictionary
        ws_dict = {'CAWKSP': CAWKSP, 'SAVE': SAVE, 'DASA': DASA, 'AUTISM': AUTISM, 'SUBT': SUBT, 'SUBP': SUBP}

        return ws_dict
    except Exception as e:
        raise ValueError("Error processing data:", e)
    
def read_and_process_SHM_data(file_path):
    """
    Read and process the CSV file containing SHM new hire data
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1', sep=',', low_memory = False)
    
        # Filter out only rows with completed workshops
        CAWKSP = df[(df['Child Abuse Workshop'] != 'In Process') & (df['Child Abuse Workshop'] != 'Not Started')]
        SAVE = df[(df['Violence Prevention Workshop'] != 'In Process') & (df['Violence Prevention Workshop'] != 'Not Started')]
        DASA = df[(df['DASA Workshop'] != 'In Process') & (df['DASA Workshop'] != 'Not Started')]

        # Store filtered dataframes in a dictionary
        shm_ws_dict = {'CAWKSP': CAWKSP, 'SAVE': SAVE, 'DASA': DASA}

        return shm_ws_dict
    except Exception as e:
        raise ValueError("Error processing SHM data:", e)
    
def plot_number_of_workshops_by_date(ws_dict):
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
    
def plot_number_of_workshops_by_counts(ws_dict, shm_ws_dict):
    """
    Plot the number of each workshop completed on SHM vs completed on TSN
    """
    try: 
        # Initialize dictionaries to store workshop counts for each type
        ws_count_dict = {}
        shm_ws_count_dict = {}
        
        # Calculate row counts for workshops completed via TSN
        for k, v in ws_dict.items():
            ws_count_dict[k] = len(v)  # Count rows in DataFrame v
        
        # Calculate row counts for workshops completed via SHM
        for k, v in shm_ws_dict.items():
            shm_ws_count_dict[k] = len(v)  # Count rows in DataFrame v

        print(ws_count_dict)
        print(shm_ws_dict)

        # Extract workshop counts for each workshop type
        TSN = [ws_count_dict['CAWKSP'], ws_count_dict['SAVE'], ws_count_dict['DASA']]
        SHM = [shm_ws_count_dict['CAWKSP'], shm_ws_count_dict['SAVE'], shm_ws_count_dict['DASA']]

        # Define parameters for bar plot
        bar_groups = 3
        bar_locs = np.arange(bar_groups)
        width = 0.2

        # Create figure and axis for plotting
        fig = plt.figure()
        ax = fig.add_subplot(111)  # Corrected to `subplots` instead of `subplot`
        
        # Plot bars for TSN and SHM workshop counts
        TSN_bars = ax.bar(bar_locs, TSN, width, color='b')
        SHM_bars = ax.bar(bar_locs + width, SHM, width, color='g')
        
        # Set labels and legend
        ax.set_ylabel('Number of Workshops Completed')
        ax.set_xticks(bar_locs + width)
        ax.set_xticklabels(('Child Abuse', 'School Violence', 'Dignity for All Students'))
        ax.legend((TSN_bars[0], SHM_bars[0]), ('Completed Through TSN', 'Overall Completed'))

        # Function to add labels on top of each bar
        def autolabel(bars):
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, 1.05 * h, '%d' % int(h), ha='center', va='bottom')
        
        # Call autolabel function for both TSN and SHM bars
        autolabel(TSN_bars)
        autolabel(SHM_bars)

        # Show the plot
        plt.show()

    except Exception as e:
        raise ValueError("Error plotting workshops:", e)


def main():
    try:
        file_path1 = select_file()
        file_path2 = select_file()
        if not file_path1:
            print("No file selected. Exiting...")
            return
        if not file_path2:
            print("No file selected. Exiting...")
            return
        ws_dict = filter_and_process_workshop_data(file_path1)
        shm_ws_dict = read_and_process_SHM_data(file_path2)
        if not ws_dict:
            print("No workshops found in the data.")
            return
        if not shm_ws_dict:
            print("No SHM data found.")
        plot_number_of_workshops_by_counts(ws_dict, shm_ws_dict)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
