# -*- coding: utf-8 -*-
"""
Created on Sat May 18 00:25:48 2019

@author: Shihao Ran
         STIM Laboratory
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May  7 20:38:19 2019

this script plot the map of games

@author: Shihao Ran
         STIM Laboratory
"""

import pandas as pd
from ast import literal_eval
import math

from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Spectral8, Pastel1, Set3
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap

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
    return df

#%%
    
games = ['overwatch',
        'Fortnite',
        'ApexLegends',
        'Hearthstone',
        'CSGO',
        'dota2',
        'LeagueOfLegends']

df = pd.read_csv(r'./dataframes/place_tweet_id_with_text.csv')
#%%
df = get_lon_lat(df, 'place')
#%%
df = add_xy_col(df)

#%%
df['circle_size'] = df.followers_count.apply(lambda x: min(30, x/(x+2000) * 30))
#%%
df = df.set_index('created_at')

#%%
colors = ['#ffa42d',#Overwatch
          '#9e3bd3',#Fortnite
          '#d23a3a',#ApexLegends
          '#f7c12c',#Hearthstone
          '#202f70',#CSGO
          '#632020',#dota2
          '#2cb4cc',#LeagueOfLegends
          ]
#%%
# this map is initialized to include the whole earth
plot = figure(plot_width=1000, plot_height=550,
           x_range=(-14000000, -7500000), y_range=(2500000, 6500000),
           x_axis_type="mercator", y_axis_type="mercator",
           tools="hover, pan, box_zoom, wheel_zoom, reset", 
           tooltips=[('user id', '@user_id'),
                     ('game', '@game'),
                     ('location', '@name'),
                     ('followers', '@followers_count'),
                     ('x','$x{0.1f}'),
                     ('y','$y{0.1f}')])

# add the tile from CARTOBPOSITRON database
CARTODBPOSITRON = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(CARTODBPOSITRON)

source = ColumnDataSource(data = {'x': df.merc_x,
                                  'y': df.merc_y,
                                  'size': df.circle_size,
                                  'name': df.name,
                                  'user_id': df.tweet_user_id,
                                  'followers_count': df.followers_count,
                                  'game': df.game})


# add circles to the map
plot.circle(x='x', y='y', size='size',
            color=factor_cmap('game', colors, games),
            legend = 'game',
            source=source, alpha=0.5)

plot.legend.orientation = "horizontal"
plot.legend.location = "bottom_center"

output_file('game_map48_us.html')
show(plot)