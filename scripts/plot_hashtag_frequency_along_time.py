# -*- coding: utf-8 -*-
"""
Created on Wed May  8 20:16:09 2019

this script plots the frequency change of the hashtags over time
for all the games

@author: Shihao Ran
         STIM Laboratory
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource

#%%
hashtags = pd.read_csv(r'C:\Users\demon\Dropbox\shihao-selfLearning\vggm\scripts\dataframes\hashtags_with_time.csv')

games = ['LeagueOfLegends',
         'Fortnite',
         'ApexLegends',
         'Hearthstone']

for game in games:
    hashtags[game] = hashtags['text'].str.contains(game)

hashtags['created_at'] = pd.to_datetime(hashtags['created_at'])

hashtags = hashtags.set_index('created_at')

game_freq = [hashtags[game].resample('1 h').mean() for game in games]



#%%
plot = figure(plot_height=250, plot_width=600,
              title='Hourly Frequency',
              tools='pan, box_zoom, reset, hover',
              tooltips=[('frequency', '@frequency')])

for index, freq in enumerate(game_freq):
    source = ColumnDataSource(data = {'hours': freq.index.hour[:-3],
                                      'frequency': freq[:-3]})
    plot.line(x='hours', y='frequency', legend=freq.name , source=source,
              color=Category10[4][index])
    
output_file('mention_freq.html')
show(plot)
