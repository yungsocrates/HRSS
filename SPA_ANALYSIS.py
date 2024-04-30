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

def read_and_process_data(file_path):
    """
    Read and process the CSV file.
    """
    df = pd.read_csv(file_path, encoding='latin1', sep=',')
    df = df[(df['Finalized on Payroll?'] == 'Y') & (df['Authorized Start Date'] != 'Not Complete')]
    df['Authorized Start Date'] = pd.to_datetime(df['Authorized Start Date'], format='%m/%d/%Y')
    return df

def plot_number_of_hires(df):
    """
    Plot the number of hires over time.
    """
    ts = df['Authorized Start Date'].value_counts().sort_index()  # Sort by date
    plt.figure(figsize=(10, 6))  # Adjust figure size
    ax = ts.plot(kind='line', marker='o', color='b')  # Customize plot
    ax.set_ylabel('Number of Hires')
    ax.set_xlabel('Date')
    ax.set_title('Number of Hires Over Time')
    ax.grid(color='gray', linestyle='dashed')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()
    return ts

def main():
    file_path = select_file()
    if not file_path:
        print("No file selected. Exiting...")
        return
    try:
        df = read_and_process_data(file_path)
        ts = plot_number_of_hires(df)
        print(ts)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
