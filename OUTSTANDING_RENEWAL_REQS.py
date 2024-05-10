import pandas as pd
import tkinter as tk
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

def filter_and_process_TSN_data(file_path):
    """
    Read and process the CSV file for TSN onboarding requirements.
    
    Args:
    file_path (str): The file path of the CSV file containing onboarding requirement data.
    
    Returns:
    pd.DataFrame: A DataFrame containing the TSN data.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='UTF-8', sep=',')
        return df
    except Exception as e:
        # Raise an error if any exception occurs during data processing
        raise ValueError(f"Error processing TSN data: {e}")

def read_and_process_SHM_data(file_path, tsn_df):
    """
    Read and process the CSV file containing SHM renewal data.
    
    Args:
    file_path (str): The file path of the CSV file containing SHM renewal data.
    tsn_df (pd.DataFrame): DataFrame containing TSN data.
    
    Returns:
    dict: A dictionary containing filtered DataFrames for each onboarding requirement type.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='latin1', sep=',', low_memory=False)

        matching_dict = {}
        for k, v in SHM_req_names.items():
            if k == 'EXAM':
                df1 = tsn_df[((tsn_df['ATAS Exam Registration'] == 'Not Complete') & (tsn_df['Passing of ATAS Exam'] == 'Not Complete'))]
                df1 = df1[df1['SSN'].isin(df['SSN'])]
                matching_dict[k] = df1[['SSN', 'ATAS Exam Registration', 'Passing of ATAS Exam']]  # Selecting only 'SSN' and column specified by 'v'
            else: 
                df1 = tsn_df[((tsn_df[v] == 'Not Attended') | (tsn_df[v] == 'Not Complete') | (tsn_df[v] == 'Exempt'))]
                df1 = df1[df1['SSN'].isin(df['SSN'])]
                matching_dict[k] = df1[['SSN', v]]  # Selecting only 'SSN' and column specified by 'v'

        return matching_dict
    except Exception as e:
        # Raise an error if any exception occurs during data processing
        raise ValueError(f"Error processing SHM data: {e}")

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
        tsn_df = filter_and_process_TSN_data(file_path1)

        # Process SHM data from the second file, using workshop data from the first file
        matching_dict = read_and_process_SHM_data(file_path2, tsn_df)

        # Check if SHM data exists
        if not matching_dict:
            print("No SHM data found.")
        else:
            print(matching_dict)

        # Export matching_dict to a CSV file
        for key, value in matching_dict.items():
            value.to_csv(f"{key}_matching_data.csv", index=False)
            print(f"Matching data for {key} exported successfully.")
        
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define SHM requirement names
    SHM_req_names = {
        'EXAM':'State Exam',
        'Child Abuse Workshop':'Child Abuse Identification',
        'Violence Prevention Workshop':'School Violence Prevention',
        'SubHub Training':'Substitute Teacher/Paraprofessional Online Training',
        'Processing Fee':'Processing Fee',
        'DASA Workshop':'DASA Workshop',
        #'TEACH':'TEACH Profile',
        'Bachelor Degree':'Bachelor\'s Degree',
        'High School Diploma':'High School Diploma',
        'Autism Workshop':'Autism Workshop'
    }

    main()
