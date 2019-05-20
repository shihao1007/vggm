# -*- coding: utf-8 -*-
"""
Created on Wed May  8 15:30:14 2019

Editor:
    Shihao Ran
    STIM Laboratory
"""

# Import the necessary modules
from bokeh.layouts import widgetbox, row, column
from bokeh.models import Slider, ColumnDataSource, LinearColorMapper
import pandas as pd
import math

from ast import literal_eval
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import curdoc
from bokeh.palettes import Viridis256, mpl
from bokeh.transform import log_cmap, factor_cmap
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
    
    return df

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # Set the yr name to slider.value and new_data to source.data
    hour = slider.value
    
    if hour < 24:
        day = 9
    elif hour < 48:
        hour -= 24
        day = 10
    else:
        hour -= 48
        day = 11
    
    time1 = '2019-05-%02d %02d' % (day, hour)
    
    new_data = {
                'x': df.loc[time1].merc_x,
                'y': df.loc[time1].merc_y,
                'size': df.loc[time1].circle_size,
                'name': df.loc[time1].name,
                'user_id': df.loc[time1].tweet_user_id,
                'followers_count': df.loc[time1].followers_count,
                'game': df.loc[time1].game,
                'color': df.loc[time1].game_colors}

    source.data = new_data
#%%
# load the dataset
games = ['overwatch',
        'Fortnite',
        'ApexLegends',
        'Hearthstone',
        'CSGO',
        'dota2',
        'LeagueOfLegends']
#%%
colors = ['#ffa42d',#Overwatch
          '#9e3bd3',#Fortnite
          '#d23a3a',#ApexLegends
          '#f7c12c',#Hearthstone
          '#202f70',#CSGO
          '#632020',#dota2
          '#2cb4cc',#LeagueOfLegends
          ]
df = pd.read_csv(r'./dataframes/place_tweet_id_with_text.csv')
#%%
df = get_lon_lat(df, 'place')
#%%
df = add_xy_col(df)

#%%
df['circle_size'] = df.followers_count.apply(lambda x: min(30, x/(x+2000) * 30))
sid = SentimentIntensityAnalyzer()
df['sentiment_score'] = df.text.apply(sid.polarity_scores).apply(lambda x: x['compound'])
#%%
df = set_time_index(df)
df['game_colors'] = df.game.apply(lambda x: {games[i]:colors[i] for i in range(len(games))}[x])
#%%
def senti_color_mapper(score, palette):
    if score < -0.5:
        return palette[0]
    elif score < 0:
        return palette[1]
    elif score == 0:
        return palette[2]
    elif score < 0.5:
        return palette[3]
    else:
        return palette[4]

def senti_level_mapper(score):
    if score < -0.5:
        return 'Highly Negative'
    elif score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    elif score < 0.5:
        return 'Positive'
    else:
        return 'Highly Positive'

df['sentiment_colors'] = df.sentiment_score.apply(lambda x: senti_color_mapper(x, mpl['Plasma'][5]))
df['sentiment_level'] = df.sentiment_score.apply(lambda x: senti_level_mapper(x))
#%%
# create a bokeh interactive plot of the map

plot = figure(plot_width=1000, plot_height=550,
           x_range=(-20000000, 20000000), y_range=(-7000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator",
           tools="hover, pan, box_zoom, wheel_zoom, reset", 
           tooltips=[('user id', '@user_id'),
                     ('game', '@game'),
                     ('location', '@name'),
                     ('followers', '@followers_count')])

# add the tile from CARTOBPOSITRON database
CARTODBPOSITRON = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(CARTODBPOSITRON)

source = ColumnDataSource(data = {'x': df.loc['2019-05-09 01'].merc_x,
                                  'y': df.loc['2019-05-09 01'].merc_y,
                                  'size': df.loc['2019-05-09 01'].circle_size,
                                  'name': df.loc['2019-05-09 01'].name,
                                  'user_id': df.loc['2019-05-09 01'].tweet_user_id,
                                  'followers_count': df.loc['2019-05-09 01'].followers_count,
                                  'game': df.loc['2019-05-09 01'].game,
                                  'color': df.loc['2019-05-09 01'].game_colors})

# add circles to the map
plot.circle(x='x', y='y', size='size',
            color='color',
            legend = 'game',
            source=source, alpha=0.5)

plot.legend.orientation = "horizontal"
plot.legend.location = "bottom_center"


# Make a slider object: slider
slider = Slider(title='Hour', start=1, end=49, step=1, value=1)

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = column(widgetbox(slider), plot)
curdoc().add_root(layout)

#show(layout)