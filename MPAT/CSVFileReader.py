import os
import pandas as pd



class CSVFileReader:
    def __init__(self, folder_path):
        """
        Initialize the CSVFileReader with the path to the folder containing CSV files.

        Parameters:
        folder_path (str): The path to the folder containing CSV files.
        """
        self.folder_path = folder_path
        self.dataframes = {}  # Dictionary to store DataFrames with file names as keys
    
    def read_csv_files_to_dataframe(self):
        """
        Read all CSV files in the specified folder into DataFrames and store them in a dictionary.

        Returns:
        dict: A dictionary where keys are file names and values are DataFrames.
        """
        # Check if the folder exists
        if not os.path.isdir(self.folder_path):
            print("Folder not found.")
            return None
        
        # Get a list of all files in the folder
        files = os.listdir(self.folder_path)
        
        # Filter out only CSV files
        csv_files = [file for file in files if file.endswith('.csv')]
        
        # If no CSV files found
        if not csv_files:
            print("No CSV files found in the folder.")
            return None
        
        # Iterate over each CSV file and read it into a DataFrame with semicolon as delimiter
        for csv_file in csv_files:
            csv_file_path = os.path.join(self.folder_path, csv_file)
            df = pd.read_csv(csv_file_path, delimiter=';')
            # Use the CSV file name as the key for easy reference
            self.dataframes[csv_file] = df
        
        return self.dataframes
    
    def get_dataframe_by_index(self, index):
        """
        Retrieve a DataFrame by its index in the dictionary.

        Parameters:
        index (int): The index of the DataFrame to retrieve.

        Returns:
        DataFrame: The DataFrame corresponding to the specified index, or None if index is invalid.
        """
        # Get the keys of the dictionary
        df_keys = list(self.dataframes.keys())
        
        # Check if index is valid
        if index < 0 or index >= len(df_keys):
            print("Invalid index.")
            return None
        
        # Get the DataFrame using the index
        selected_key = df_keys[index]
        return self.dataframes[selected_key]
    
    def save_dataframe_to_csv(self, index, save_path):
        """
        Save a DataFrame to a CSV file.

        Parameters:
        index (int): The index of the DataFrame to save.
        save_path (str): The path where the CSV file will be saved.

        Returns:
        bool: True if the DataFrame was saved successfully, False otherwise.
        """
        # Retrieve the DataFrame by index
        df = self.get_dataframe_by_index(index)
        
        # Check if DataFrame exists
        if df is None:
            return False
        
        # Save the DataFrame to a CSV file
        df.to_csv(save_path, index=False)
        return True
