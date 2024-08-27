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

# License:
Attribution-NonCommercial-NoDerivatives 4.0 International
