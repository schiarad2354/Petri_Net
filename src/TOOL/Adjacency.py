import os
import pandas as pd
import networkx as nx


class AdjacencyMatrix:
    def __init__(self, adjacency_file, US=True, stateabrev=None):
        """
        Initialize the AdjacencyMatrix class.
        Purpose: Given user/pre-defined adjacency file, returns the adjacency file as pandas dataframe.
        This is to ensure the file is formatted correctly for input into SIRSBML for large-scale Petri Net model configuration.
        
        Parameters:
        - adjacency_file: Path to the adjacency file (CSV or JSON).
        - US: Boolean flag indicating if US county data is used (default True).
        - stateabrev: List of state abbreviations to filter data (default None).
        """
        self.adjacency_file = adjacency_file
        self.US = US
        self.stateabrev = stateabrev
    
    def detect_file_type_by_extension(self, file_path):
        """
        Detects whether the file is a CSV or JSON file.
        
        Parameters:
        - file_path: Path to the file whose extension needs to be checked.
        
        Returns:
        - 'csv' if the file is a CSV.
        - 'json' if the file is a JSON.
        - None if the file type is neither CSV nor JSON.
        """
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.json':
            return "json"
        elif file_extension.lower() == '.csv':
            return "csv"
        else:
            return None

    def create_tuples(self, df):
        """
        Removes duplicates and creates tuples from DataFrame columns.
        
        Parameters:
        - df: DataFrame containing columns to convert into tuples.
        
        Returns:
        - List of tuples derived from unique pairs of values in the DataFrame.
        """
        all_tuples = list(df.itertuples(index=False, name=None))
        final_tuples = []
        for tpl in all_tuples:
            if (tpl[1], tpl[0]) not in final_tuples and tpl[1] != tpl[0]:
                final_tuples.append((str(tpl[0]), str(tpl[1])))
        return final_tuples
    
    def generate_adjacency_matrix(self):
        """
        Generates the adjacency matrix from the input adjacency file.
        
        Returns:
        - Pandas DataFrame representing the adjacency matrix.
        """
        if self.US:
            try:
                adj_df = pd.read_json('US_County_Adjacency_Table.json')
                
                if self.stateabrev is not None:
                    # Filter by state abbreviation if provided
                    adj_df = adj_df[adj_df['State Name'].isin(self.stateabrev)]
                
                # Create tuples for easier handling in creating the graph
                GEOID_tuples = self.create_tuples(adj_df[['County GEOID', 'Neighbor GEOID']])
                
                G = nx.Graph()  # Initialize graph
                G.add_edges_from(GEOID_tuples)  # Add the edges 

                adj_matrix = nx.to_pandas_adjacency(G) # creates adjacency matrix as a pandas dataframe
                return adj_matrix
            
            except FileNotFoundError:
                print(f"{self.adjacency_file} not found.")
                return None
        else:
            file_type = self.detect_file_type_by_extension(self.adjacency_file)
            if not file_type:
                raise ValueError("Not supported file type. Must be either CSV or JSON.")
            
            try:
                if file_type == 'csv':
                    adj_df = pd.read_csv(self.adjacency_file)
                elif file_type == 'json':
                    adj_df = pd.read_json(self.adjacency_file)
                
                # Create tuples for easier handling in creating the graph
                GEOID_tuples = self.create_tuples(adj_df[['County GEOID', 'Neighbor GEOID']])
                
                G = nx.Graph()  # Initialize graph
                G.add_edges_from(GEOID_tuples)  # Add the edges 

                adj_matrix = nx.to_pandas_adjacency(G) #creates adjacency matrix as a pandas dataframe
                return adj_matrix
            
            except FileNotFoundError:
                print(f"{self.adjacency_file} not found.")
                return None

            
            
## Example usage
##adjacency_file = 'US_County_Adjacency_Table.json'
#adjacency_file = 'example.json'
#adjacency_matrix = AdjacencyMatrix(adjacency_file, US=True, stateabrev=['TX'])
#adj_df = adjacency_matrix.generate_adjacency_matrix()
#adj_df