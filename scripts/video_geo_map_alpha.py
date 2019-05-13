# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:36:52 2019

plot geographical information onto a Bokeh map plot
using CARTOBDPOSITRON map

NOTE that the longitudinal and latitudinal information is not
consistant in the tweets database
for geo, the first value in the list is the latitude
for coordinates and places, the first value is the longitude

@author: Shihao Ran
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
from bokeh.palettes import mpl, Viridis256
from bokeh.transform import linear_cmap
import numpy as np

from nltk.sentiment.vader import SentimentIntensityAnalyzer
#%%
def set_time_index(df):
    """
    set the created_at column as the index
    """
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at')
    
    return df
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


#%%
#%%
# load the dataset
place = pd.read_csv(r'.\dataframes\place_tweet_id_with_text.csv')
# reset index
place = set_time_index(place)
# get lon and lat info
place = get_lon_lat(place, 'place')
# convert them into x y coordinates and add to the original dataframe
add_xy_col(place)
# add circle size column
place['circle_size'] = place['followers_count'].apply(lambda x: min(25, x/(x+2000) * 25))
# add sentiment info based on text
# initialize the analyzer
sid = SentimentIntensityAnalyzer()
place['sentiment_score'] = place.text.apply(sid.polarity_scores).apply(lambda x: x['compound'])
#%%
# create a bokeh interactive plot of the map

# this map is initialized to include the whole earth
plot = figure(plot_width=600, plot_height=300, title='Geosptial Map of Tweets',
           x_range=(-20000000, 20000000), y_range=(-7000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator",
           tools="hover, pan, box_zoom, wheel_zoom, reset", tooltips=[('user', '@name'),
                                    ('location', '@full_name'),
                                    ('followers', '@followers_count'),
                                    ('sentiment', '@sentiment_score')])

# add the tile from CARTOBPOSITRON database
CARTODBPOSITRON = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(CARTODBPOSITRON)

source = ColumnDataSource(data = {'x': place.merc_x,
                                  'y': place.merc_y,
                                  'size': place.circle_size,
                                  'name': place.name,
                                  'full_name': place.full_name,
                                  'followers_count': place.followers_count,
                                  'sentiment_score': place.sentiment_score})


# add circles to the map
plot.circle(x='x', y='y', size='size', color=linear_cmap('sentiment_score', mpl['Plasma'][5], -1, 1),
         source=source, alpha=0.65)



# output the html file and show the plot in a browser
output_file('geo_map.html')
show(plot)