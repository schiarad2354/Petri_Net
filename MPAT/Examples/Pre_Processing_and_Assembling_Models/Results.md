# Pre Processing and Assembling of Models

Here, we show scalability of the pre-processing steps that MPAT performs. In particular, the elapsed time it takes to create a grid from a shapefile and generate the corresponding SBML file of epidemiological models following Section 3.2 and generalization of Figure 5 in the manuscript. We do this for various selected countries and U.S. states. For computing resources, the simulations were conducted on an Intel Xeon Gold 6226R CPU @ 2.90Ghz with 64 threads and 512 GB of memory om a Linux server. 

## Selected Countries
Without loss of generalization, we randomly selected the following countries:
- Serbia
- China
- Saudi Arabia
- Brazil
- Egypt
- Canada

The following figure shows the elapsed time (in seconds) for the time it takes to generate the grid of the country's shapefile and create the corresponding SBML file. We observe that as the grid size becomes more granular, the processing time increases. This is because finer grids involve a greater number of grid points, leading to more detailed computations and a higher volume of data to manage. Consequently, as the granularity intensifies, the computational resources required grow, resulting in longer processing times. In addition, there is heterogeneity of processing times by country. For example, the shapefile for Egypt takes longer to process than China's, despite China being a much larger country. This discrepancy can be attributed to the complexity and detail of the shapefile data, such as the number of polygons, the level of geometric detail, or the presence of intricate boundaries. A detailed analysis of this phenomena is out-of-the scope of this showcase.

![Execution_Time_Country](https://github.com/user-attachments/assets/ce434a97-612c-4390-a04a-e0ccc62e2907)


### Selected Country Shapefile and Grid
For completeness, below are the selected country's shapefile plots and corresponding grid for Grid_Size = 100.

#### Serbia (SRB)




#### China (CHN)




#### Saudi Arabia (SAU)




#### Brazil (BRA)




#### Egypt (EGY)




#### Canada (CAN)



## Selected U.S. States
Without loss of generalization, we randomly selected the following U.S. states:
- Texas
- Arizona
- California
- Illinois
- Georgia
- Michigan
- New York

![Execution_Time_US_States](https://github.com/user-attachments/assets/acc5f5d2-6329-4a60-b8ae-d95334c61bdf)


### Selected U.S. State Shapefile and Grid
For completeness, below are the selected U.S. state's shapefile plots and corresponding grid for Grid_Size = 250.

#### Texas (TX)




#### Arizona (AZ)




#### California (CA)




#### Illinois (IL)




#### Georgia (GA)




#### Michigan (MI)




#### New York


