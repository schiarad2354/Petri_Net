import pandas as pd
from Polygon import Polygon
from Adjacency import Adjacency

class InfLayers:
    """
    This class handles the import and processing of information layers from a vector format CSV file with pre-defined areas.
    """
    
    def __init__(self, information_layers_dataframe, polygon_input=None, adjacency_input=None, adjacency_file=None):
        """
        Initializes the InfLayers class with provided inputs.

        Parameters:
        - information_layers_dataframe (str): Path to the CSV file containing information layers.
        - polygon_input (str, optional): Path to the shapefile for polygon input.
        - adjacency_input (str, optional): Not used, included for future extension.
        - adjacency_file (str, optional): Path to the adjacency matrix file.
        """
        # Load the information layers dataframe from the provided CSV file
        self.information_layers_dataframe = pd.read_csv(information_layers_dataframe)
        
        # Initialize input parameters
        self.polygon_input = polygon_input
        self.adjacency_input = adjacency_input
        self.adjacency_file = adjacency_file

        # If polygon input is provided, process it
        if self.polygon_input is not None:
            try:
                # Create a Polygon object and generate grid and adjacency matrix
                polygon_grid = Polygon(self.polygon_input, grid_size=10, US=True, stateabrev=['AZ'])
                self.grid, self.adj_matrix = polygon_grid.get_grid_and_adj_matrix(hexagonal=False)
            except FileNotFoundError:
                print("Shapefile not found.")
                self.grid = None
                self.adj_matrix = None

        # If adjacency input is provided, process it
        elif self.adjacency_input is not None:
            try:
                # Create an Adjacency object using the provided adjacency file
                adj_grid = Adjacency(self.adjacency_file, US=True, stateabrev=['TX'])
                self.adj_grid = adj_grid
            except FileNotFoundError:
                print("InfLayers: Adjacency matrix file not found.")
                self.adj_grid = None
        else:
            print("InfLayers: No input found.")
            self.grid = None
            self.adj_matrix = None
            self.adj_grid = None

    def process_layers(self):
        """
        Processes the information layers by performing element-wise multiplication with the grid or adjacency data.

        Returns:
        - pd.DataFrame: Processed grid or adjacency data with multiplied values.
        """
        # If grid data is available, process it
        if self.grid is not None:
            # Perform element-wise multiplication with information layers
            self.grid['grid_cell'] = self.grid['grid_cell_mix'] * self.information_layers_dataframe.iloc[:, 1:].values
            return self.grid

        # If adjacency grid data is available, process it
        elif self.adj_grid is not None:
            # Perform element-wise multiplication with information layers
            self.adj_grid['grid_cell'] = self.adj_grid['grid_cell_mix'] * self.information_layers_dataframe.iloc[:, 1:].values
            return self.adj_grid

        # If neither grid nor adjacency grid data is available, print an error message
        else:
            print("InfLayers: cannot multiply.")
            return None

# Usage example:
# inf_layers = InfLayers('information_layers_dataframe.csv', polygon_input='cb_2023_us_county_500k.shp')
# processed_grid = inf_layers.process_layers()
