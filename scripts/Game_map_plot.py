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

from bokeh.plotting import figure, show, output_notebook
from bokeh.tile_providers import get_provider, Vendors

#%%

geo = pd.read_csv(r'E:\self_learning\vggm\dataframes\geo.csv')


def merc(Coords):
    if Coords[:3] == '[[[':
        Coordinates = literal_eval(Coords)
        lon = Coordinates[0][0][0]
        lat = Coordinates[0][0][1]
    else:
        Coordinates = literal_eval(Coords)
        lon = Coordinates[1]
        lat = Coordinates[0]
    
    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + lat * (math.pi/180.0)/2.0)) * scale
    return [(x, y), (lon, lat)]

#%%
locations = []
for item in geo['coordinates'].tolist():
    try:
        locations.append(merc(item))
    except:
        pass

x = [point[0] for point in locations]
y = [point[1] for point in locations]

#%%

#coordinates['coords_x'] = coordinates['coordinates'].apply(lambda x: merc(x)[0])
#coordinates['coords_y'] = coordinates['coordinates'].apply(lambda x: merc(x)[1])

p = figure(plot_width=1000, plot_height=550,
        x_range=(-20000000, 20000000), y_range=(-7000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator")


CARTODBPOSITRON = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(CARTODBPOSITRON)

p.circle(x = x, y = y)
output_notebook()
show(p)