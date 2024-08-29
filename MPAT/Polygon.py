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
    - countryiso (list, optional): List of country ISO 3166-1 alpha-3 codes to filter. The shapefile of all the countries across the world (except for U.S. since this is already taken care of). Defaults to None.
    - hex_grid (bool, optional): Flag indicating whether to use the square grid(False) or hexagonal grid (True). Default is False.
    - overlap (bool, optional): Flag indicating whether grid cells can overlap polygon boundaries. Defaults to True.
    - crs (str, optional): Coordinate reference system (CRS) of the shapefile. Defaults to "EPSG:4326".
    
    Returns: 
    - Geopandas dataframe of grid cells
    - Correspondingadjacency matrix
    """
    def __init__(self, shapefile_path, grid_size, US = False, stateabrev = None, countryiso = None, overlap = True, crs="EPSG:4326"):
        # Cannot use both U.S. and country's shapefiles
        if countryiso is not None and US:
            raise ValueError("US cannot be True when countryiso is not None.")
        if countryiso is None and not US:
            raise ValueError("US cannot be False when countryiso is None.")
            
        self.shapefile_path = shapefile_path
        self.grid_size = int(np.ceil(np.sqrt(grid_size)))
        self.US = US
        self.stateabrev = stateabrev
        self.countryiso = countryiso
        self.overlap = overlap
        self.crs = crs
        self.gdf = self.polygoninitialization()

    def polygoninitialization(self):
        """
        Initialize GeoDataFrame from the shapefile based on class parameters.
        
        Returns:
        - gdf (GeoDataFrame): GeoDataFrame containing polygon geometries.
        """
        if self.shapefile_path:
            try:
                # Load shapefile
                gdf = gpd.read_file(self.shapefile_path)
                gdf = gdf.to_crs(epsg=4326)
                return gdf
            
            except FileNotFoundError as e:
                print(f"File not found: {e.filename}")
                return None
            
        if not self.shapefile_path:
            # If Non-U.S., use World shapefile and filter by country or countries of interest
            if self.countryiso is not None:
                try:
                    # filter for the shapefiles of every country in the world shapefile 
                    gdf = gpd.read_file("World_Countries.shp") # reads shapefile of countries
                    gdf.to_crs(epsg=4326, inplace=True) # converts the CRS to EPSG:4326 for consitency
                
                    # Preprocessing for cleaning
                    gdf = gdf[gdf['COUNTRY'] != 'Clipperton'] # This is an uninhabitated French island: https://www.cia.gov/the-world-factbook/countries/clipperton-island/: so we remove it
                    gdf = gdf[gdf['COUNTRY'] != 'United States'] # We have specific shapefile that includes U.S. states, so this is handled differently
                
                    # Mapping Country ISO ids.
                    # NOTE: This code uses the Alpha-3 code e.g. AFG, ALB, DZA, etc. We refer to the following for a complete list: https://www.iso.org/obp/ui/#search
                    # NOTE: ISO_CC.json contains these Alpha-3 codes
                    Country_ISO = pd.read_json('ISO_CC.json') # imports the ISO of each country (along with country name and continent)
                    ISO_values = Country_ISO[Country_ISO['ISO_CC'].isin(self.countryiso)] # maps the input ISO values to those in the shapefile for constency
                    gdf = gdf[gdf['ISO_CC'].isin(ISO_values['ISO_CC'])]  # returns geopandas dataframe of selected countries
                    gdf = gdf.reset_index(drop=True) 
                
                    return gdf
            
                except FileNotFoundError as e:
                    print(f"File not found: {e.filename}")
                    return gdf
                
            # If U.S.
            if self.US:
                try:
                    gdf = gpd.read_file("cb_2023_us_county_500k.shp") # reads shapefile of U.S.
                    gdf.to_crs(epsg=4326, inplace=True) # converts the CRS to EPSG:4326 for consitency
                    # filter for contiguous US states excluding Alaska (02) and Hawaii (15)
                    gdf = gdf[(pd.to_numeric(gdf['STATEFP']) < 60) & (pd.to_numeric(gdf['STATEFP']) != 2) & (pd.to_numeric(gdf['STATEFP']) != 15)]
                    gdf['STATEFP'] = gdf['STATEFP'].astype(int) # convert STATEFP to int for indexing
                 
                except FileNotFoundError:
                    print("US Shapefile not found.")
                
                # If U.S. and U.S. State
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
            
        # Handle case where shapefile_path is empty and countryiso and US is None
        return None
        
        
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
        
        
        # Calculate the total area covered by each cell interesecting the county
        total_area = sum(grid['geometry'].intersection(county['geometry']).area 
                     for _, county in intersecting_grid_cells.iterrows())
        
        # Saves the GEOID and corresponding proportion as a dictionary
        grid_cell_mix = {}

        if total_area == 0:
            for county_id in intersecting_grid_cells['GEOID']:
                #print("Total area of intersection is zero.")
                grid_cell_mix[county_id] = 0 # Sets column to zero for all GEOIDs.        
        
        else:
            # If total area is nonzero, calculate the proportion that cell of the GEOIDs i.e. intersecting polygons
            for _, county in intersecting_grid_cells.iterrows():
                intersection_area = grid['geometry'].intersection(county['geometry']).area # calculates the intersection area of the cell geometry with the county geometry
                proportion = intersection_area / total_area # calculates the proportion of the cell intersection area of the cell geometry with the county geometry
                grid_cell_mix[county['GEOID']] = proportion # stores the proportion
            
        return grid_cell_mix
    
        
        
    def create_hex_grid(self):
        """
        Create hexagonal grid over geometry.

        Returns:
        - grid (GeoDataFrame): GeoDataFrame of hexagonal grid polygons.
        """
        lon_min, lat_min, lon_max, lat_max = self.gdf.total_bounds

        # Calculate cell size to get approximately the desired number of grid cells
        hexagon_size = (lon_max - lon_min) / self.grid_size

        hexagon_height_ratio = np.sin(np.pi / 3)
        longitude_cols = np.arange(np.floor(lon_min), np.ceil(lon_max), 3 * hexagon_size)
        latitude_rows = np.arange(np.floor(lat_min) / hexagon_height_ratio, np.ceil(lat_max) / hexagon_height_ratio, hexagon_size)

        hexagons = []
        for longitude_col in longitude_cols:
            for row_index, hexagon_y_position in enumerate(latitude_rows):
                if (row_index % 2 == 0):
                    hexagon_x_start = longitude_col
                else:
                    hexagon_x_start = longitude_col + 1.5 * hexagon_size

                hexagons.append(shapely.geometry.Polygon([
                    (hexagon_x_start, hexagon_y_position * hexagon_height_ratio),
                    (hexagon_x_start + hexagon_size, hexagon_y_position * hexagon_height_ratio),
                    (hexagon_x_start + (1.5 * hexagon_size), (hexagon_y_position + hexagon_size) * hexagon_height_ratio),
                    (hexagon_x_start + hexagon_size, (hexagon_y_position + (2 * hexagon_size)) * hexagon_height_ratio),
                    (hexagon_x_start, (hexagon_y_position + (2 * hexagon_size)) * hexagon_height_ratio),
                    (hexagon_x_start - (0.5 * hexagon_size), (hexagon_y_position + hexagon_size) * hexagon_height_ratio),
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
        
        if self.US:
            try:
                # Get mixture of counties of U.S. (since given U.S. shapefile has this)
                grid['grid_cell_mix'] = grid.apply(self.get_grid_cell_mix, axis=1)
                grid = grid.reset_index(drop=True)
                return grid
            
            except Exception as e: 
                print(f"An error occurred while processing U.S. grid cells: {e}")
            
        else:
            return grid


    def create_grid(self):
        """
        Create square grid that covers a geodataframe area or a fixed boundary with latitude-longitude coordinates.

        Returns:
        - grid (GeoDataFrame): GeoDataFrame of grid polygons.
        """
        # Determine bounds
        lon_min, lat_min, lon_max, lat_max = self.gdf.total_bounds

        # Calculate cell size to get approximately the desired number of grid cells
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
            
            
        if self.US:
            try:
                # Get mixture of counties of U.S. (since given U.S. shapefile has this)
                grid['grid_cell_mix'] = grid.apply(self.get_grid_cell_mix, axis=1)
                grid = grid.reset_index(drop=True)
                return grid
            
            except Exception as e: 
                print(f"An error occurred while processing U.S. grid cells: {e}")
            
        else:
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
    
    
    def get_grid_and_adj_matrix(self, hexagonal = False):
        if hexagonal:
            grid = self.create_hex_grid()
        else:
            grid = self.create_grid()
            
        if grid is None or grid.empty:
            print("Grid creation failed or returned an empty geopandas dataframe.")
            return None, None
        
        adj_df = self.calculate_adjacency_matrix(grid)
        return grid, adj_df

#polygon_grid = Polygon(shapefile_path = None, grid_size = 3, US = True, stateabrev = ['AZ'])
#grid, adj_df = polygon_grid.get_grid_and_adj_matrix(hexagonal = False)
#grid
    
# For U.S.
#polygon_grid = Polygon(shapefile_path = None, grid_size = 3, US = True, stateabrev = ['AZ'])
#grid, adj_df = polygon_grid.get_grid_and_adj_matrix(hexagonal = False)
#grid

# For Non U.S.
#polygon_grid = Polygon(shapefile_path = None, grid_size = 50, US = False, countryiso = ['SRB']) # for Serbia
#grid, adj_df = polygon_grid.get_grid_and_adj_matrix(hexagonal = False)
#grid