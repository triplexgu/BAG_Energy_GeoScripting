#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: Assessing the monumental state of buildings to enable more targeted energy transition on a household level.
Team: Teal_panther
Number of the topic chosen (or "own"): 6
"""
## Imports ##
import os
import urllib.request
import geopandas as gpd
import json
from owslib.wfs import WebFeatureService
import folium
import math
import pandas as pd

## Predefined functions ##
## Do not change ##

# Download the data and save it
def DownloadData(url,status,bbox):
    # make sure there is a data directory
    datadir = './data'
    if not os.path.exists(datadir):
        os.makedirs(datadir)    
    # add code here to download data from wherever it is hosted
    fn = datadir + '/'+status+'.gml'
    if not os.path.isfile(fn):
        urllib.request.urlretrieve(url, fn)
    
    # Read in again with GeoPandas
    GDF = gpd.read_file(fn)
    #Ref: https://stackoverflow.com/questions/42751748/using-python-to-project-lat-lon-geometry-to
    GDF=GDF.to_crs({'init': 'epsg:28992'})
    #Ref: https://geopandas.org/en/stable/gallery/plot_clip.html
    GDF_clip=GDF.clip(bbox)
    return GDF_clip

# Get the data from wfs
def GetWFSData(url,layer_num,x,y):
    xmin,ymin,xmax,ymax=x-150,y-150,x+150,y+150
    wfs_bag = WebFeatureService(url=url, version='2.0.0')
    layer = list(wfs_bag.contents)[layer_num] #First layer
    # Get the features for the study area
    response = wfs_bag.getfeature(typename=layer, bbox=(xmin, ymin, xmax, ymax), outputFormat='json')
    data = json.loads(response.read())
    
    # Create GeoDataFrame, without saving first
    GDF= gpd.GeoDataFrame.from_features(data['features'])
    GDF.crs=28992
    return GDF

# Get the monumental buildings dataframe
# Call the function defined above
def GetDataframe(x,y,cell_distance=150): # the central point of each grid
    # Set the bbox for datasets
    xmin, xmax, ymin, ymax = x -cell_distance, x + cell_distance, y - cell_distance, y + cell_distance
    bbox=(xmin, xmax, ymin, ymax)
    
    # Download data from websits
    #ProvincialGDF = DownloadData("https://service.pdok.nl/provincies/provinciale-monumenten/atom/downloads/inspire-pv-ps.nlps-pm.gml","Provincial",bbox)
    GDF_Municipal = DownloadData("https://map.data.amsterdam.nl/maps/monumenten?REQUEST=GetFeature&SERVICE=wfs&typename=monument_coordinaten&outputformat=geojson&VERSION=2.0.0&SRSNAME=EPSG:4326","Municipal",bbox)
    
    # Filter the municipal monuments
    GDF_Municipal= GDF_Municipal.loc[GDF_Municipal.monumentstatus=='Gemeentelijk monument', :]
    GDF_Municipal = GDF_Municipal[["geometry","id","monumentstatus"]]
    
    # Get BAG data
    GDF0_bag=GetWFSData('https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS',0,x,y)
    GDF3_bag=GetWFSData('https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS',3,x,y)
    
    GDF0_bag = GDF0_bag[['geometry', 'identificatie', 'bouwjaar', 'status', 'gebruiksdoel']]
    GDF3_bag = GDF3_bag[['geometry', 'postcode', 'huisnummer', 'huisletter', 'toevoeging', 'woonplaats']]
    
    BAG_complete = gpd.sjoin(GDF0_bag, GDF3_bag, how='inner')
    # Perform an intersection overlay
    # Ref: https://gis.stackexchange.com/questions/446712/select-polygons-by-location-of-points-using-geopandas
    BAG_complete  = BAG_complete.dissolve(by=['identificatie','huisnummer'])
    BAG_complete = BAG_complete .reset_index()
    BAG_complete  = BAG_complete .drop('index_right', axis=1)
    
    # Get the stadsgezicht data
    GDF_stads=GetWFSData('https://services.rce.geovoorziening.nl/rce/wfs?request=GetCapabilities',0,x,y)
    GDF_stads = GDF_stads[['geometry', 'STATUS', 'RIJKSMONNR']]
    
    # Get the national monument data
    GDF_national=GetWFSData('https://data.geo.cultureelerfgoed.nl/openbaar/wfs?service=WFS&request=GetCapabilities',2,x,y)
    GDF_national = GDF_national[["geometry","ID","juridische_status"]]
    
    # Select national monumental buildings
    InterNation= gpd.sjoin(BAG_complete , GDF_national, how='inner', predicate='contains')
    # Remove the duplicate indecies
    # Ref: https://stackoverflow.com/questions/13035764/remove-pandas-rows-with-duplicate-indices
    InterNation= InterNation[~InterNation.index.duplicated(keep='first')]
    # Transfer data type from int64 into str
    InterNation['ID'] = InterNation['ID'].astype('str')
    # Assign the id and monumental status for different monumental buildings
    # Ref: https://medium.com/analytics-vidhya/pandas-how-to-change-value-based-on-condition-fc8ee38ba529
    BAG_complete['national_monument']=list(BAG_complete.contains(InterNation))
    BAG_complete.loc[BAG_complete["national_monument"] == True, "national_monument_id"] = InterNation["ID"]
    
    # Add municipal monuments information to the original BAG dataframe
    InterMuni= gpd.sjoin(BAG_complete , GDF_Municipal, how='inner', predicate='contains')
    InterMuni= InterMuni[~InterMuni.index.duplicated(keep='first')]
    BAG_complete['municipal_monument']=list(BAG_complete.contains(InterMuni))
    BAG_complete.loc[BAG_complete["municipal_monument"] == True, "municipal_monument_id"] = InterMuni["id"]
    
    # Add beschermd_stadsgezicht information to the original BAG dataframe
    InterStads= gpd.sjoin(BAG_complete , GDF_stads, how='inner', predicate='contains')
    InterStads= InterStads[~InterStads.index.duplicated(keep='first')]
    InterStads['RIJKSMONNR'] = InterStads['RIJKSMONNR'].astype('str')
    BAG_complete['beschermd_stadsgezicht']=list(BAG_complete.contains(InterStads))
    BAG_complete.loc[BAG_complete["beschermd_stadsgezicht"] == True, "beschermd_stadsgezicht_id"] = InterStads["RIJKSMONNR"]
    
    # Drop other buildings which are not monumental
    Monument_building=[]
    for row in range(len(BAG_complete)):
        if any(list(BAG_complete[['municipal_monument','national_monument','beschermd_stadsgezicht']].iloc[row]))==True:
            Monument_building+=[True]
            row+=1
        else:
            Monument_building+=[False]
            row+=1
    
    BAG_complete=BAG_complete[Monument_building]
    
    # Change the True or False to yes or no in beschermd_stadsgezicht
    BAG_complete.loc[BAG_complete["beschermd_stadsgezicht"] == True, "beschermd_stadsgezicht"] = "yes"
    BAG_complete.loc[BAG_complete["beschermd_stadsgezicht"] == False, "beschermd_stadsgezicht"] = "no"

    return BAG_complete

# Add energy transition values for monumental buildings
def AddHeatingpumps(GDF):
    #change the column names(monumental status) to the name corresponding to the dataframe.
    #are heating pumps allowed?
    # Ref:https://stackoverflow.com/questions/19211828/using-any-and-all-to-check-if-a-list-contains-one-set-of-values-or-another
    # Ref:https://warmtepompenadvies.nl/warmtepomp-vergunning/
    are_heating_pumps_allowed = []
    x= GDF[['municipal_monument','national_monument','beschermd_stadsgezicht']]
    for row in range(len(x)):
      if any(a == True for a in list(x.iloc[row]))==True:
        are_heating_pumps_allowed.append('yes, but an "omgevingsvergunning" is required')
      elif any(a == 'yes' for a in list(x.iloc[row]))== True:
        are_heating_pumps_allowed.append('yes, but an "omgevingsvergunning" is required')
      else:
        are_heating_pumps_allowed.append('yes, heating pumps are allowed')

    GDF['HP allowed'] = are_heating_pumps_allowed

    #are hybrid heating pumps recommended?
    # Ref:https://www.engie.nl/product-advies/warmtepomp/orientatie/vragen/is-mijn-huis-geschikt 
    are_heating_pumps_recommended =[]
    for row in list(GDF['bouwjaar']):
      if row <= 1975: 
        are_heating_pumps_recommended.append('No')
      elif row >= 1976 and row < 1992:
        are_heating_pumps_recommended.append('No')
      elif row >= 1992 and row < 2000:
        are_heating_pumps_recommended.append('Yes')
      else:
        are_heating_pumps_recommended.append('Yes')
        
    GDF['HHP recommended'] = are_heating_pumps_recommended

    #are full electric heating pumps recommended?
    # Ref:https://www.engie.nl/product-advies/warmtepomp/orientatie/vragen/is-mijn-huis-geschikt 
    are_elec_heating_pumps_recommended =[]
    for row in list(GDF['bouwjaar']):
      if row <= 1975: 
        are_elec_heating_pumps_recommended.append('No')
      elif row >= 1976 and row < 1992:
        are_elec_heating_pumps_recommended.append('No')
      elif row >= 1992 and row < 2000:
        are_elec_heating_pumps_recommended.append('No')
      else:
        are_elec_heating_pumps_recommended.append('Yes')
        
    GDF['EHP recommended'] = are_elec_heating_pumps_recommended
    return GDF

# Rename the columns name to English 
def RenameColNames(GDF):
    # Rename the dataframe columns names
    GDF.rename(columns={'identificatie':'pand_id'}, inplace=True)
    GDF.rename(columns={'huisnummer':'house_number'}, inplace=True)
    GDF.rename(columns={'bouwjaar':'building_startdate'}, inplace=True)
    GDF.rename(columns={'gebruiksdoel':'utility'}, inplace=True)
    GDF.rename(columns={'postcode':'postal_code'}, inplace=True)
    GDF.rename(columns={'huisletter':'house_letter'}, inplace=True)
    GDF.rename(columns={'toevoeging':'house_number_suffix'}, inplace=True)
    GDF.rename(columns={'woonplaats':'city'}, inplace=True)
    return GDF

# Combine the horizonal tiles
def HorizontalMap(h_length,central,cell_size=300):
    # Set the cell distance
    cell_distance=cell_size/2
    # Calculate the tiles number
    num_horizon=math.floor(h_length/cell_size)
    # Get the first file
    hor_all=GetDataframe(round(central[0]),round(central[1]),cell_distance)
    hor_all=AddHeatingpumps(hor_all)
    hor_all=RenameColNames(hor_all)
    #x1,y1=round(central[0]),round(central[1])
    #hor_all=func.GetWFSData('https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS',0,x1,y1)
    # combine all horizontal tiles 
    for i in range(num_horizon-1):
        central=(central[0]+cell_size,central[1])
        hor_new=GetDataframe(round(central[0]),round(central[1]),cell_distance)
        hor_new=AddHeatingpumps(hor_new)
        hor_new=RenameColNames(hor_new)
        #x1+=cell_size
        #hor_new=func.GetWFSData('https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS',0,x1,y1)
        i+=1
        hor_all=pd.concat([hor_all,hor_new])
    return hor_all

# Join the vertical maps
def AllMap(v_length,h_length,central_points,cell_size=300):
    central=central_points
    num_vertical=math.floor(v_length/cell_size)

    map_all=HorizontalMap(h_length,central, cell_size)
    for i in range(num_vertical-1):
        central=(central[0],central[1]+cell_size)
        ver_new=HorizontalMap(h_length,central, cell_size)
        i+=1
        map_all=pd.concat([map_all,ver_new])

    return map_all

# define color
def colr(word):
    '''´
    this function is to take word as input, 
    then return the color str based on the input value.
    
    Parameters
    -----------
    word : str
           it refers to the content of each cell
           from one column of dataframe
    
    Returns
    ----------
    col: str
         the color decision for visualization
    '''
    if word == 'Yes':
        col = 'red'
    elif word == 'No':
        col = 'gray'
    return col

# create an html map
def CreateMap(df, a, b,name):
    '''
    This function is to make an interactive map of input dataframe,
    inllustrating monumental buildings' HP-assemble suggestions.

    Parameters
    ----------
    df : GeoDataFrame
        The dataframe is from main script, which extracts the monumental
        buildings'info and HP recommendations.
    x : float
        The longitude of central point.
    y : float
        The latitude of central point.

    Returns
    -------
    The interactive map will be automatically saved under /output file,
    in HTML format.

    '''
    
    # Re-project
    df = df.to_crs(4326) # WGS84
    # get centroids of each polygon
    # shift the order of x/y
    # REF: https://gis.stackexchange.com/questions/166820/returning-lat-and-long-of-centroid-point-with-geopandas
    
    df['x'] = df['geometry'].centroid.map(lambda p:p.y)
    df['y'] = df['geometry'].centroid.map(lambda p:p.x)
    # initialize map
    base_map = folium.Map(location=[a, b], 
                          zoom_start=15,
                          control_scale=True,
                          tiles='Stamen Terrain')
    # add layer to map
    # REF: https://www.youtube.com/watch?v=Ftczp3bx1uw
    hhp_feature = folium.FeatureGroup('HHP recommended').add_to(base_map)
    ehp_feature = folium.FeatureGroup('EHP recommended').add_to(base_map)

    for x,y,hhp,ehp,allow,post,date in zip(df['x'],df['y'],df['HHP recommended'],df['EHP recommended'],df['HP allowed'],df['postal_code'],df['building_startdate']):
        target_str = 'postal code is: {}<br> Building year:{}<br> Allow reqirement:{}'.format(post,date,allow)
        hhp_feature.add_child(folium.Marker(location=[x,y],
                                            popup = folium.Popup(target_str, max_width=1000,max_height=1000),
                                            icon=folium.Icon(color=colr(hhp),shadow_size=(0,0))))
        ehp_feature.add_child(folium.Marker(location=[x,y],
                                            popup = folium.Popup(target_str,max_width=1000,max_height=1000),
                                            icon=folium.Icon(color=colr(ehp),shadow_size=(0,0))))
    # add legends
    # REF: https://stackoverflow.com/questions/65042654/how-to-add-categorical-legend-to-python-folium-map
    import branca
    legend_html = '''
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px;
    left: 50px;
    width: 250px;
    height: 80px;
    z-index:9999;
    font-size:14px;
    ">
    <p><a style="color:#FF0000;font-size:150%;margin-left:20px;">&diams;</a>&emsp;Recommended</p>
    <p><a style="color:#808080;font-size:150%;margin-left:20px;">&diams;</a>&emsp;Unsuitable</p>
</div>
<div style="
    position: fixed; 
    bottom: 50px;
    left: 50px;
    width: 150px;
    height: 80px; 
    z-index:9998;
    font-size:14px;
    background-color: #ffffff;

    opacity: 0.7;
    ">
</div>
{% endmacro %}
'''
    legend = branca.element.MacroElement()
    legend._template = branca.element.Template(legend_html)
    # set title
    # ref: https://github.com/python-visualization/folium/issues/1202
    title_html='''
    <h3 align="center" style="font-size:20px"><b>Which kind of HP is recommended for monumental buildings?</b></h3>
    '''
    # add layercontrol
    folium.map.LayerControl('topleft',
                            collapsed=False,
                            max_height=1500,
                            max_width=1500).add_to(base_map)
    base_map.get_root().add_child(legend)
    base_map.get_root().html.add_child(folium.Element(title_html))
    # save map into HTML
    base_map.save('output/'+name+'.html')