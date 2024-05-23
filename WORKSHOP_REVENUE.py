import pandas as pd
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
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
            'SUBP':'Sub Paraprofessional Online Training',
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


def plot_number_of_workshops_by_revenue(ws_dict):
    try:
        # Initialize dictionaries to store workshop dollar revenue amounts for each type
        ws_revenue_dict = {}
        for k, v in ws_dict.items():
            # Remove dollar sign ('$') and commas (',') from 'Amount' column and convert to numeric
            v['Amount'] = v['Amount'].replace('[\$,]', '', regex=True).astype(float)
            ws_revenue_dict[k] = v['Amount'].sum()

        print(ws_revenue_dict)
        
        # Calculate the total sum of revenue
        total_revenue = sum(ws_revenue_dict.values())

        # Extract revenue for each workshop type
        TSN = [ws_revenue_dict['CAWKSP'], ws_revenue_dict['SAVE'], ws_revenue_dict['DASA'], ws_revenue_dict['AUTISM'], ws_revenue_dict['SUBP'], ws_revenue_dict['SUBT']]

        # Add a fifth bar for the total sum
        TSN.append(total_revenue)

        # Get today's date
        today = date.today()

        # Define parameters for bar plot
        bar_groups = 7  # Updated to include the fifth bar
        bar_locs = np.arange(bar_groups)
        width = 0.2

        # Create figure and axis for plotting
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title(label=f'Revenue by Workshop from {today.month}-{today.day}-{today.year-1}')

        # Plot bars for TSN and SHM workshop counts
        TSN_bars = ax.bar(bar_locs, TSN, width, color=['b', 'b', 'b', 'b', 'b', 'b', 'r'])  # Set the color of the fifth bar to red
        
        # Set labels and legend
        ax.set_ylabel('Revenue in USD (millions)')
        ax.set_xticks(bar_locs)
        ax.set_xticklabels(('Child Abuse', 'School Violence', 'Dignity for All Students', 'Autism Workshop', 'Sub Para Online Training', 'Sub Teacher Online Training', 'Total'))
        ax.grid(axis='y', color='k', linestyle='--')

        # Function to add labels on top of each bar
        def autolabel(bars):
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h, f'${h:,.2f}', ha='center', va='bottom')

        # Call autolabel function for all bars
        autolabel(TSN_bars)

        # Show the plot
        plt.show()

    except Exception as e:
        raise ValueError("Error plotting workshops:", e)

def main():
    try:
        # Select files
        file_path = select_file()  # Select the first CSV file

        # Check if files are selected
        if not file_path:
            print("No file selected. Exiting...")
            return

        # Process workshop data from the first file
        ws_dict = filter_and_process_workshop_data(file_path)

        # Check if workshop data exists
        if not ws_dict:
            print("No workshops found in the data.")
            return

        # Plot the number of workshops completed via TSN and SHM
        plot_number_of_workshops_by_revenue(ws_dict)

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
