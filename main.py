#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: Assessing the monumental state of buildings to enable more targeted energy transition on a household level.
Team: Teal_panther
Number of the topic chosen (or "own"): 6

main scripts:
1. Input the x,y coordinates and the length of vertical and horizontal axis by users
2. Transfer the longitude and latitude to UTM
3. Call function to get the BAG data and monumental data, then return the result of monumental building dataframe
4. Interate the extent to combine all tiles of maps
5. Plot the map
6. Output the map into local directory
"""
import Python.project_func as func
from pyproj import Proj, transform
import os

# Input the extent lengths
print("\nPlease check the README file for more information.\n")

print("Here are some lon/lat coordinates you can choose from:")
print("The ZOO of Artis: 4.915601, 52.365728 \nDe Oude Kerk: 4.8978013069, 52.3742407533 \nRijksmuseum: 4.8848174843,52.3597641312 \nUniversity of Amsterdam: 4.895479,52.368893 \n")
x= float(input("X coordinate in longitude:"))
y= float(input("Y coordinate in latitude:"))

print("\n---------- !!! The length should be a multiple of 300 !!! -----------\n")
print("Recommended horizontal and vertical lengths for the points are provided in the README file.\n")
h_length=float(input("The horizontal length of the extent:"))
v_length=float(input("The vertical length of the extent:"))

# Copy the original longitude and latitude data to use it for creating the map later
a = y
b = x

# Reprojection 
# WGS84 in degrees and not RD new in meters
# Ref: https://gis.stackexchange.com/questions/280292/converting-epsg2263-to-wgs84-using-python-pyproj
inProj = Proj("+init=EPSG:4326") 
outProj  = Proj("+init=EPSG:28992")
# Transfer the log&lat to UTM 
x,y=transform(inProj,outProj,x,y)

# Set the cell size
cell_size = 300
cell_distance=cell_size/2

# Scan from the left bottom cell and set the central points coordinates
central_points=(x-(h_length/2)+cell_distance,y-(v_length/2)+cell_distance)

# First, combine all horizontal tiles for each row
# Then, join the rows
# Call the function to get the large scale map
map_am=func.AllMap(v_length,h_length,central_points, cell_size=300)

# Plot the map
maplayer=map_am.plot()
maplayer.set_xlim(x-(h_length/2), x+(h_length/2))
maplayer.set_ylim(y-(v_length/2), y+(v_length/2))

# Save map to disk
if not os.path.exists('./output'):
    os.makedirs('./output')  

# Define your output json file name
print("\nThe outputs will be a geojson file which contains the vector data for monument buildings, and an interactive map.")
print("The input below should not have any special characters.")
file_name=input('\nPlease input the name for the ouput files:')
map_am.to_file('./output/'+file_name+'.geojson', driver='GeoJSON')

# Create the html map of specified area 
func.CreateMap(map_am,a,b,file_name)
