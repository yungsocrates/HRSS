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
    
    Args:
    file_path (str): The file path of the CSV file containing workshop data.
    
    Returns:
    dict: A dictionary containing filtered dataframes for each workshop type.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1', sep=',')

        # Filter out rows where the 'Payment Source' is not 'Waived'
        df = df[df['Payment Source'] != 'Waived']

        # Filter dataframes for each workshop type
        ws_names = {
            'CAWKSP':'Child Abuse Workshop',
            'SAVE':'School Violence Prevention Workshop',
            'DASA':'Dignity for All Students Act (DASA)',
            'AUTISM':'Autism Workshop',
            'SUBT':'Sub Teacher Online Training',
            'SUBP':'Sub Para Online Training',
        }

        ws_dict = {}
        for k, v in ws_names.items():
            if k == 'CAWKSP':
                # Special case for 'Child Abuse Workshop' where we include both old and new program
                ws_dict[k] = df[((df['Workshop Name'] == v) | (df['Workshop Name'] == f'{v} (New Program)'))]
            else:
                # For other workshops, filter based on workshop name only
                ws_dict[k] = df[(df['Workshop Name'] == v)]

        return ws_dict
    except Exception as e:
        # Raise an error if any exception occurs during data processing
        raise ValueError("Error processing TSN data:", e)

def read_and_process_SHM_data(file_path):
    """
    Read and process the CSV file containing SHM new hire data
    
    Args:
    file_path (str): The file path of the CSV file containing SHM new hire data.
    
    Returns:
    dict: A dictionary containing filtered dataframes for each workshop type.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1', sep=',', low_memory=False)
    
        # Filter out only rows with completed workshops
        shm_ws_names = {
            'CAWKSP': 'Child Abuse Workshop',
            'SAVE': 'Violence Prevention Workshop',
            'DASA': 'DASA Workshop',
        }

        shm_ws_dict = {}
        for k, v in shm_ws_names.items():
            # Filter out rows where the workshop status is 'Complete'
            shm_ws_dict[k] = df[df[v] == 'Complete']

        return shm_ws_dict
    except Exception as e:
        # Raise an error if any exception occurs during data processing
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
        # Filter ws_dict by shm_ws_dict SSNs (i.e. vlookup)
        for k, v in shm_ws_dict.items():
            df = ws_dict[k]
            df = df[df['SSN'].isin(v['SSN'])]
            ws_dict[k] = df

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
        ax = fig.add_subplot(111)
        plt.title(label='Workshops Completed via TSN')
        
        # Plot bars for TSN and SHM workshop counts
        TSN_bars = ax.bar(bar_locs, TSN, width, color='b')
        SHM_bars = ax.bar(bar_locs + width, SHM, width, color='r')
        
        # Set labels and legend
        ax.set_ylabel('Number of Workshops Completed')
        ax.set_xticks(bar_locs +0.5*width)
        ax.set_xticklabels(('Child Abuse', 'School Violence', 'Dignity for All Students'))
        ax.legend((TSN_bars[0], SHM_bars[0]), ('Completed Through TSN', 'Overall Completed'), loc='lower right')

        # Function to add labels on top of each bar
        def autolabel(bars):
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h, '%d' % int(h), ha='center', va='bottom')
        
        # Call autolabel function for both TSN and SHM bars
        autolabel(TSN_bars)
        autolabel(SHM_bars)

        # Show the plot
        plt.show()

    except Exception as e:
        raise ValueError("Error plotting workshops:", e)


def main():
    try:
        # Select files
        file_path1 = select_file()  # Select the first CSV file
        file_path2 = select_file()  # Select the second CSV file

        # Check if files are selected
        if not file_path1 or not file_path2:
            print("No file selected. Exiting...")
            return

        # Process workshop data from the first file
        ws_dict = filter_and_process_workshop_data(file_path1)

        # Process SHM data from the second file, using workshop data from the first file
        shm_ws_dict = read_and_process_SHM_data(file_path2)

        # Check if workshop data exists
        if not ws_dict:
            print("No workshops found in the data.")
            return
        if not shm_ws_dict:
            print("No SHM data found.")

        # Plot the number of workshops completed via TSN and SHM
        plot_number_of_workshops_by_counts(ws_dict, shm_ws_dict)

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
