# -*- coding: utf-8 -*-
"""
Created on Tue May  7 12:25:17 2019

this script visualize the number of tweets for all the games
with stacked bar chart, different types of tweets are highlighted

@author: Shihao Ran
         STIM Laboratory
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.palettes import Blues3, Greens3, Oranges3, Reds3
from bokeh.palettes import BuPu3, PuRd3, Purples3, YlGnBu3, Spectral3
from bokeh.plotting import figure
from bokeh.layouts import column

#%%
# load the dataframe
df = pd.read_csv(r'.\dataframes\hashtags_48_with_quoted_or_retweeted.csv')
#%%
# specify the games and types
games = ['GrandTheftAutoV',
        'LeagueOfLegends',
        'Fortnite',
        'dota2',
        'CSGO',
        'ApexLegends',
        'Hearthstone',
        'overwatch']

types = ['quote', 'retweet', 'original']

#colors = [Blues3, Greens3, Oranges3, Reds3,
#          BuPu3, PuRd3, Purples3, YlGnBu3]

# count the numbers of different types of games
original = []
retweets = []
quoted = []
for game in games:
    original.append(((df.game==game)&(df.if_retweeted==False)&(df.if_quoted==False)).sum())
    retweets.append(df['if_retweeted'][(df.game==game) & (df.if_retweeted==True)].sum())
    quoted.append(df['if_quoted'][(df.game==game) & (df.if_quoted==True)].sum())

# scale the numbers by a log10 function
original_scaled = np.log10(original)
retweets_scaled = np.log10(retweets)
quoted_scaled = np.log10(quoted)

# calculate the total number of tweets
total = [original[i] + retweets[i] + quoted[i] for i in range(len(original))]

# sort the names
sorted_games = sorted(games, key=lambda x: total[games.index(x)])
#%%

# plot the figures
output_file("game_dist_bar_fancy.html")

before_scale = {'games' : games,
               'original': original,
               'retweet': retweets,
               'quote': quoted}

after_scale = {'games' : games,
               'original': original_scaled,
               'retweet': retweets_scaled,
               'quote': quoted_scaled}

p1 = figure(y_range=sorted_games, plot_height=250, plot_width=1000,
           title="Number of Tweets for Each Game",
           toolbar_location=None, tools="hover",
           tooltips="$name @games: @$name")

p1.hbar_stack(types, y='games', height=0.9, color=Blues3, source=ColumnDataSource(before_scale),
             legend=["%s " % x for x in types])

p2 = figure(y_range=sorted_games, plot_height=250, plot_width=1000,
           title="Number of Tweets for Each Game (log10)",
           toolbar_location=None, tools="hover",
           tooltips="$name @games: @$name")

p2.hbar_stack(types, y='games', height=0.9, color=Blues3, source=ColumnDataSource(after_scale),
             legend=["%s scaled" % x for x in types])

p1.y_range.range_padding = 0.1
p1.ygrid.grid_line_color = None
p1.legend.location = "bottom_right"
p1.axis.minor_tick_line_color = None
p1.outline_line_color = None

p2.y_range.range_padding = 0.1
p2.ygrid.grid_line_color = None
p2.legend.location = "bottom_right"
p2.axis.minor_tick_line_color = None
p2.outline_line_color = None
show(column(p1, p2))
