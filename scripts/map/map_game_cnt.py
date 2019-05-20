# -*- coding: utf-8 -*-
"""
Created on Sat May 18 01:03:34 2019

this script generates a bar chart of the number of tweets shown on the map
for all the games, respectively.

@author: Shihao Ran
         STIM Laboratory
"""

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap

import pandas as pd
import numpy as np

# load the dataframe
df = pd.read_csv(r'./dataframes/map_game_cnt.csv')
# convert columns into lists
count = df['count'].tolist()
games = df.game.tolist()
# sort the game names by the number of counts
games = sorted(games, key=lambda x: -count[games.index(x)])
# specify colors
colors = [
          '#9e3bd3',#Fortnite
          '#d23a3a',#ApexLegends
          '#ffa42d',#Overwatch
          '#2cb4cc',#LeagueOfLegends
          '#632020',#dota2
          '#202f70',#CSGO
          '#f7c12c',#Hearthstone
          ]

# create a column data source
source = ColumnDataSource(data=dict(game=games, count=count, color=colors))

# plot the figure
p = figure(x_range=games, plot_height=300, plot_width=1000,
           toolbar_location=None,
           tools='hover', tooltips=('@game: @count'),
           title="Game Counts")
p.vbar(x='game', top='count', width=0.5, line_color='white', source=source,
       fill_color='color', legend='game')

p.xgrid.grid_line_color = None
p.legend.orientation = "horizontal"
p.legend.location = "top_center"

# output and show
output_file("map_game_cnt.html")
show(p)
