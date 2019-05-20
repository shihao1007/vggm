# -*- coding: utf-8 -*-
"""
Created on Sat May 18 01:03:34 2019

@author: Shihao Ran
         STIM Laboratory
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May 15 19:13:13 2019

this script plot the language distribution

@author: Shihao Ran
         STIM Laboratory
"""

from bokeh.io import show, output_file
from bokeh.plotting import figure
#from bokeh.palettes import Category7
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap

import pandas as pd
import numpy as np

#%%
df = pd.read_csv(r'./dataframes/map_game_cnt.csv')
#%%
count = df['count'].tolist()
games = df.game.tolist()
games = sorted(games, key=lambda x: -count[games.index(x)])
#%%
colors = [
          '#9e3bd3',#Fortnite
          '#d23a3a',#ApexLegends
          '#ffa42d',#Overwatch
          '#2cb4cc',#LeagueOfLegends
          '#632020',#dota2
          '#202f70',#CSGO
          '#f7c12c',#Hearthstone
          ]

source = ColumnDataSource(data=dict(game=games, count=count, color=colors))

p = figure(x_range=games, plot_height=300, plot_width=1000,
           toolbar_location=None,
           tools='hover', tooltips=('@game: @count'),
           title="Game Counts")
p.vbar(x='game', top='count', width=0.5, line_color='white', source=source,
       fill_color='color', legend='game')

p.xgrid.grid_line_color = None
p.legend.orientation = "horizontal"
p.legend.location = "top_center"
output_file("map_game_cnt.html")
show(p)