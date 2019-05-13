# -*- coding: utf-8 -*-
"""
Created on Wed May  8 15:30:14 2019

Editor:
    Shihao Ran
    STIM Laboratory
"""

# Import the necessary modules
from bokeh.layouts import widgetbox, row, column
from bokeh.models import Slider, ColumnDataSource
import pandas as pd
import math

from ast import literal_eval
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import curdoc
from bokeh.palettes import Viridis256
from bokeh.transform import log_cmap
import numpy as np

#%%
def get_lon_lat(df, geo_type):
    """
    Get longitude and latitude from the dataframe
    Append two new columns into the original dataframe
    
    Parameters
    ----------
        df: pandas dataframe
            input dataframe containing geographical information
        geo_type: string
            the type of the geographical dataframe
    
    Returns
    -------
        df: pandas dataframe
            with longitude and latitude extracted
    """
    
    # if the input dataframe is geo
    if geo_type == 'geo':
        # then the longitude is the second value in the list
        df['longitude'] = df['coordinates'].apply(lambda x: literal_eval(x)[1])
        # and the latitude is the first value
        df['latitude'] = df['coordinates'].apply(lambda x: literal_eval(x)[0])
    
    # if the input dataframe is coordinates
    elif geo_type == 'coordinates':
        # it is the other way around
        # NOTE: geo and coordinates contains the same information
        df['longitude'] = df['coordinates'].apply(lambda x: literal_eval(x)[0])
        df['latitude'] = df['coordinates'].apply(lambda x: literal_eval(x)[1])
        
    # if the input dataframe is place
    # then list contains 4 points of a bounding box
    # we need to calculate the centroid of the bounding box
    elif geo_type == 'place':
        # define a function to extract the centroid
        def get_centroid(row):
            
            # literalize the str to a list
            lst = literal_eval(row)
            
            # get the minimal and maximal latitude
            lat0 = lst[0][0][1]
            lat1 = lst[0][1][1]
            # calculate the center
            lat = (lat0 + lat1)/2
            
            # same for the longitude
            lon0 = lst[0][0][0]
            lon1 = lst[0][2][0]
            lon = (lon0 + lon1)/2
            
            # return the centroid
            return (lon, lat)
        # apply the defined function to the whole dataset
        df['longitude'] = df['coordinates'].apply(lambda x: get_centroid(x)[0])
        df['latitude'] = df['coordinates'].apply(lambda x: get_centroid(x)[1])
        
    # return the new dataset with longitude and latitude as new columns
    return df

def lonlat2merc(row):
    """
    Convert the longitude and latitude of a geographical point to
    x and y coordinates on a Mercator projected map
    
    Parameters
    ----------
    
        row: float, one row of a pandas dataframe
            Before apply this function to a dataframe
            make sure the dataframe contains two columns correspond
            to longitudinal and latitudinal numbers
    
    Returns
    -------
        (x, y): float tuple
            x and y coordinates of the points
    """
    
    # extract longitudinal and latitudinal info out of the dataframe row
    lon = row.iloc[0]
    lat = row.iloc[1]
    
    # do the conversion
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + lat * (math.pi/180.0)/2.0)) * scale
    
    # return the X and Y coordinates
    return (x, y)

def add_xy_col(df):
    # simple function that calls the Merc conversion function to each row
    # and save x and y seperately to the dataframe
    df['merc_x'] = df[['longitude', 'latitude']].apply(lambda x: lonlat2merc(x)[0], axis=1)
    df['merc_y'] = df[['longitude', 'latitude']].apply(lambda x: lonlat2merc(x)[1], axis=1)

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # Set the yr name to slider.value and new_data to source.data
    hour = slider.value
    time1 = pd.to_datetime('2019-04-23 %02d' % hour)
    time2 = pd.to_datetime('2019-04-23 %02d' % (hour+1))
    
    new_data = {
                'x': place_user.loc[time1:time2].merc_x,
                'y': place_user.loc[time1:time2].merc_y,
                'size': place_user.loc[time1:time2].circle_size,
                'name': place_user.loc[time1:time2].name,
                'full_name': place_user.loc[time1:time2].full_name,
                'followers_count': place_user.loc[time1:time2].followers_count}
    source.data = new_data
#%%
# load the dataset
place = pd.read_csv(r'.\dataframes\place.csv')
place = get_lon_lat(place, 'place')

# convert them into x y coordinates and add to the original dataframe
#add_xy_col(geo)
add_xy_col(place)
#add_xy_col(coordinates)

# load in size information from the user_info dataset
user_info = pd.read_csv(r'.\dataframes\user_info.csv')

place_user = pd.concat([place, user_info], axis=1)
place_user['circle_size'] = place_user['followers_count'].apply(lambda x: min(30, x/(x+2000) * 30))

# load time info
tweet_time = pd.read_csv(r'.\dataframes\tweet_time.csv')

# concat time info into the dataframe
time_col = pd.to_datetime(tweet_time['created_at'])

# set index as time
place_user['time'] = time_col
place_user.set_index('time', inplace=True)
#%%
# create a bokeh interactive plot of the map

# this map is initialized to include the whole earth
plot = figure(plot_width=1000, plot_height=550,
           x_range=(-20000000, 20000000), y_range=(-7000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator",
           tools="hover, pan, box_zoom, wheel_zoom, reset", tooltips=[('user', '@name'),
                                    ('location', '@full_name'),
                                    ('followers', '@followers_count')])

# add the tile from CARTOBPOSITRON database
CARTODBPOSITRON = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(CARTODBPOSITRON)

source = ColumnDataSource(data = {'x': place_user.loc['2019-04-23 02'].merc_x,
                                  'y': place_user.loc['2019-04-23 02'].merc_y,
                                  'size': place_user.loc['2019-04-23 02'].circle_size,
                                  'name': place_user.loc['2019-04-23 02'].name,
                                  'full_name': place_user.loc['2019-04-23 02'].full_name,
                                  'followers_count': place_user.loc['2019-04-23 02'].followers_count})


# add circles to the map
plot.circle(x='x', y='y', size='size', color=log_cmap('size', Viridis256, 0, 30),
         source=source, alpha=0.75)


# output the html file and show the plot in a browser
#output_file('geo_map.html')
#show(plot)

# Make a slider object: slider
slider = Slider(title='Hour', start=2, end=23, step=1, value=2)

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = column(widgetbox(slider), plot)
curdoc().add_root(layout)

output_file('slider_map.html')
show(layout)