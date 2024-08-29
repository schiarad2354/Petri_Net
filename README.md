# MPAT: Modular Petri Net Assembly Toolkit

We present a Python package called Modular Petri Net Assembly Toolkit
(MPAT) that empowers users to easily create large-scale, modular Petri
Nets for various spatial configurations, including extensive spatial grids or
those derived from shape files, augmented with heterogeneous information
layers. Petri Nets are powerful discrete event system modeling tools in computational
biology and engineering. However, their utility for automated
construction of large-scale spatial models has been limited by gaps in existing
modeling software packages. MPAT addresses this gap by supporting the
development of modular Petri Net models with flexible spatial geometries.

# Requirements
Python Dependencies:
- Python = 3.8+
- Geopandas = 0.12.2+
- Pandas = 2.0.3+
- NumPy = 1.24.3+
- Shapely = 2.0.1+
- lxml = 4.9.3+
- networkx = 3.1+

import geopandas as gpd
import pandas as pd
import numpy as np
import shapely.geometry
import xml.etree.ElementTree as ET
import networkx as nx
from itertools import product
import os
import subprocess
from contextlib import suppress
from multiprocessing import Pool

# How to install:
- Clone the repository
  https://github.com/schiarad2354/Petri_Net.git
- Install the requirements
- Run the MPAT application

# Note:
If shapefiles such as "World_Countries.shp" are missing they can be downloaded at: [https://hub.arcgis.com/datasets/ac80670eb213440ea5899bbf92a04998/explore]. Download Shapefile.zip and extract all. Ensure that they are in the correct file path for running. For U.S. if shapefile "cb_2023_us_county_500k.shp" is missing, download zipfile at [https://catalog.data.gov/dataset/2023-cartographic-boundary-file-kml-county-and-equivalent-for-united-states-1-500000/resource/2ccd7a0b-0752-4395-87ed-ee3762c37204]. 

# Usage Overview:
To begin, the user inputs the choice of a shapefile for a geographic area or the adjacency file as a CSV file of predefined patches. If it is a shapefile, Polygon.py generates a grid of patches of the user's desired size and outputs the GeoPandas data frame of the grid and adjacency matrix. On the other hand, if the adjacency matrix file is already defined by the user, then we proceed directly to the Petri Net modeling component of the toolkit. Additionally, the user input of information layers flows into \emph{InfLayers.py} for linking with the grid of patches from Polygon.py or adjacency matrix. Given the adjacency matrix either from Polygon.py or the user, SIRModelSBML.py generates the Petri Net model with desired input parameters, such as the initial number of tokens/markings for each patch and the arc weights between the patches. For the initialization of one instance of the parameters, such as tokens/markings, the user can import a CSV file with the corresponding name of the place (transition) and the number of tokens/markings (arc weight). For places that are not specified, the default token/marking is zero, and the default arc weight is one for transitions. If no CSV is imported, then the default settings of 100 tokens/markings in the first place of the order of the Petri Net are assigned, and the default arc weight of the transitions is one. The output is the corresponding Petri Net model in XML/SBML and ANDL file formats. Generating the SBML and ANDL files uses Python's built-in xml.etree submodule. These files are the reference configuration files for parallelizable or multi-scale modeling for user-defined hyperspace of parameter values in HyperParameters.py. Given the Petri Net model files, RunThroughSpike.py runs each file through the Petri Net simulator, Spike. The output of RunThroughSpike.py is a collection of CSV files of the resulting simulation results for each simulation run. Because of the unwieldy number of CSV files produced by executing multiple runs, CSVFileReader.py compiles all of the CSV files into a single \blue{one}, creating an automatic directory and providing a basic analysis of the results. Since the files are in CSV format, they can be exported to a variety of software applications by the user.

# License:
Attribution-NonCommercial-NoDerivatives 4.0 International
