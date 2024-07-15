import geopandas as gpd
import pandas as pd
import numpy as np
import shapely.geometry



class Polygon:
    """
    A class to handle polygon operations and grid generation based on shapefile data.
    Purpose: Given user shapefile, create grid over the shapefile and the corresponding adjacency matrix. 
    This will be used as an input for Petri Net model configuration.

    Parameters:
    - shapefile_path (str): Path to the shapefile containing polygon geometries.
    - grid_size (int): Number of grid cells to generate.
    - US (bool, optional): Flag indicating whether the shapefile is for US states. Defaults to True.
    - stateabrev (list, optional): List of state abbreviations to filter if US is True. Defaults to None.
    - overlap (bool, optional): Flag indicating whether grid cells can overlap polygon boundaries. Defaults to True.
    - crs (str, optional): Coordinate reference system (CRS) of the shapefile. Defaults to "EPSG:4326".
    
    Returns: 
    - Geopandas dataframe of grid cells
    - Correspondingadjacency matrix
    """
    def __init__(self, shapefile_path, grid_size, US=True, stateabrev=None, overlap=True, crs="EPSG:4326"):
        self.shapefile_path = shapefile_path
        self.grid_size = grid_size
        self.US = US
        self.stateabrev = stateabrev
        self.overlap = overlap
        self.crs = crs
        self.gdf = self.polygoninitialization()

    def polygoninitialization(self):
        """
        Initialize GeoDataFrame from the shapefile based on class parameters.
        
        Returns:
        - gdf (GeoDataFrame): GeoDataFrame containing polygon geometries.
        """
        # Load shapefile
        gdf = gpd.read_file(self.shapefile_path)
        gdf = gdf.to_crs(epsg=4326)
        
        if self.US:
            try:
                 # filter for contiguous US states excluding Alaska (02) and Hawaii (15)
                gdf = gdf[(pd.to_numeric(gdf['STATEFP']) < 60) & (pd.to_numeric(gdf['STATEFP']) != 2) & (pd.to_numeric(gdf['STATEFP']) != 15)]
                gdf['STATEFP'] = gdf['STATEFP'].astype(int) # convert STATEFP to int for indexing
                 
            except FileNotFoundError:
                print("US Shapefile not found.")
            
            if self.stateabrev is not None:
                # If US shapefile and user wants to select certain state
                try:
                    STATE_NAMES = pd.read_json('State_Names.json')  # imports the State_name, Abbreviation, and STATEFP (as id)
                    STATE_NAMES['STATEFP'] = STATE_NAMES['STATEFP'].astype(int)  # Convert to int for pointer
                    statefp_values = STATE_NAMES[STATE_NAMES['Abrev'].isin(self.stateabrev)]['STATEFP'].values  # maps the input abbreviations to the corresponding STATEFP
                    gdf = gdf[gdf['STATEFP'].isin(statefp_values)]  # returns geopandas dataframe of statefps
                    gdf = gdf.drop(columns=['LSAD', 'ALAND', 'AWATER'])
                    gdf = gdf.reset_index(drop=True)
                    return gdf
                    
                except FileNotFoundError:
                    print("State_Names.json file missing or not found.")
                    return gdf
            
            else:
                return gdf # if no state selected, then return US geopandas dataframe
                
        else:
            return gdf # if not US shapefile, then return US geopandas dataframe
        
        
    def get_grid_cell_mix(self, grid):
        """
        Calculate distribution of grid cell coverage over polygons.
        
        Parameters:
        - grid (GeoDataFrame): Grid cell geometry to calculate distribution over polygons.

        Returns:
        - grid_cell_mix (dict): Dictionary with grid cell distribution for each GEOID.
        """
        intersecting_grid_cells = self.gdf[self.gdf.intersects(grid['geometry'])]
        if len(intersecting_grid_cells) == 0:
            return None
        total_area = intersecting_grid_cells['geometry'].unary_union.area
        grid_cell_mix = {}
        # If total area is 0
        if total_area == 0:
            for county_id in intersecting_grid_cells['GEOID']:
                grid_cell_mix[county_id] = 0
            return grid_cell_mix
        # If total area is nonzero
        for index, county in intersecting_grid_cells.iterrows():
            intersection_area = grid['geometry'].intersection(county['geometry']).area
            proportion = 1 - intersection_area / total_area
            grid_cell_mix[county['GEOID']] = proportion
            
        return grid_cell_mix
        
        
    def create_hex_grid(self):
        """
        Create hexagonal grid over geometry.

        Returns:
        - grid (GeoDataFrame): GeoDataFrame of hexagonal grid polygons.
        """
        lon_min, lat_min, lon_max, lat_max = self.gdf.total_bounds

        unit = (lon_max - lon_min) / self.grid_size
        a = np.sin(np.pi / 3)
        cols = np.arange(np.floor(lon_min), np.ceil(lon_max), 3 * unit)
        rows = np.arange(np.floor(lat_min) / a, np.ceil(lat_max) / a, unit)

        hexagons = []
        for col in cols:
            for i, y in enumerate(rows):
                if (i % 2 == 0):
                    x0 = col
                else:
                    x0 = col + 1.5 * unit

                hexagons.append(shapely.geometry.Polygon([
                    (x0, y * a),
                    (x0 + unit, y * a),
                    (x0 + (1.5 * unit), (y + unit) * a),
                    (x0 + unit, (y + (2 * unit)) * a),
                    (x0, (y + (2 * unit)) * a),
                    (x0 - (0.5 * unit), (y + unit) * a),
                ]))

        grid = gpd.GeoDataFrame({'geometry': hexagons}, crs=self.crs)
        grid["grid_area"] = grid.area
        grid = grid.reset_index().rename(columns={"index": "grid_id"})
        grid['ID'] = range(1, len(grid) + 1)
        # Overlap of areas
        if self.overlap:
            cols = ['grid_id', 'geometry', 'grid_area']
            grid = grid.sjoin(self.gdf, how='inner').drop_duplicates('geometry')
            grid['ID'] = range(1, len(grid) + 1)
            
        grid['grid_cell_mix'] = grid.apply(self.get_grid_cell_mix, axis=1)
        return grid


    def create_grid(self):
        """
        Create square grid that covers a geodataframe area or a fixed boundary with latitude-longitude coordinates.

        Returns:
        - grid (GeoDataFrame): GeoDataFrame of grid polygons.
        """
        # Determine bounds
        lon_min, lat_min, lon_max, lat_max = self.gdf.total_bounds

        # Calculate cell size
        cell_size = (lon_max - lon_min) / self.grid_size

        # Create grid cells
        grid_cells = [
            shapely.geometry.box(lon0, lat0, lon0 + cell_size, lat0 + cell_size)
            for lon0 in np.arange(lon_min, lon_max + cell_size, cell_size)
            for lat0 in np.arange(lat_min, lat_max + cell_size, cell_size)
        ]

        grid = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=self.crs)
        grid['ID'] = range(1, len(grid) + 1)

        # Handle overlap
        if self.overlap:
            grid = grid.sjoin(self.gdf, how='inner').drop_duplicates('geometry')
            grid['ID'] = range(1, len(grid) + 1)
        grid['grid_cell_mix'] = grid.apply(self.get_grid_cell_mix, axis=1)

        return grid
    
    
    def calculate_adjacency_matrix(self, grid):
        """
        Calculate adjacency matrix for given grid.

        Parameters:
        - grid (GeoDataFrame): Grid polygons for which adjacency matrix is calculated.

        Returns:
        - adj_df (DataFrame): DataFrame representing adjacency matrix.
        """
        n = len(grid)
        adj_matrix = np.zeros((n, n), dtype=int)
        
        # Moore Neighborhood
        for i in range(n):
            for j in range(i + 1, n):
                if grid.iloc[i].geometry.touches(grid.iloc[j].geometry):
                    adj_matrix[i, j] = 1
                    adj_matrix[j, i] = 1

        adj_df = pd.DataFrame(adj_matrix, index=range(1, n+1), columns=range(1, n+1))
        return adj_df
    
    
    def get_grid_and_adj_matrix(self, hexagonal=False):
        if hexagonal:
            grid = self.create_hex_grid()
        else:
            grid = self.create_grid()
        adj_df = self.calculate_adjacency_matrix(grid)
        return grid, adj_df
    
    
    
    
    
#polygon_grid = Polygon("cb_2023_us_county_500k.shp", grid_size = 10, US = True, stateabrev = ['AZ'])
#grid, adj_df = polygon_grid.get_grid_and_adj_matrix(hexagonal=False)
#grid
