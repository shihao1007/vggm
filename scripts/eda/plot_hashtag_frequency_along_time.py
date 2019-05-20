# -*- coding: utf-8 -*-
"""
Created on Wed May  8 20:16:09 2019

this script plots the frequency change of the hashtags over time
for the top4 games

@author: Shihao Ran
         STIM Laboratory
"""

# import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool

#%%
# load the dataframe
hashtags = pd.read_csv(r'.\dataframes\hashtags_with_time.csv')

# specify the names of the games
games = ['Fortnite',
         'ApexLegends',
         'overwatch',
         'LeagueOfLegends']

# add columns to the dataframe
# that indicates if the record is about one specific game or not
for game in games:
    hashtags[game] = hashtags['hashtag'].str.contains(game, case=False)

# set time as index
hashtags['created_at'] = pd.to_datetime(hashtags['created_at'])
hashtags = hashtags.set_index('created_at')

# resample all the tweets and calculate the mean
game_freq = [hashtags[game].resample('1 h').mean() for game in games]

# define the hover tool
hover = HoverTool(
            tooltips=[
                    ('game', '@game'),
                    ('time', '@hours{%F:%r}'),
                    ('frequency', '@frequency{%0.2f}'),
                    ],
            formatters={
                    'hours': 'datetime',
                    'frequency': 'printf',
                    },
            mode='mouse'
        )

#%%
# plot all the lines
plot = figure(plot_height=400, plot_width=1000,
              title='Hourly Frequency',
              tools=[hover],
              toolbar_location=None)

for index, freq in enumerate(game_freq):
    freq_df = freq.to_frame()
    freq_df['game'] = freq.name
    source = ColumnDataSource(data = {'hours': pd.date_range(freq.index[0], freq.index[-1], len(freq)),
                                      'frequency': freq,
                                      'game': freq_df['game']})
    plot.line(x='hours', y='frequency', legend=freq.name , source=source,
              color=Category10[4][index], line_width=2)

# set the tickers
plot.xaxis.formatter = DatetimeTickFormatter(days = ['%m-%d,%r'],
                                             hours = ['%m-%d,%r'],
                                             months = ['%m-%d,%r'])
plot.xaxis.major_label_orientation = -np.pi/4-np.pi/16
plot.xaxis[0].ticker.desired_num_ticks = 8
plot.legend.orientation = "horizontal"
plot.legend.location = "top_center"
output_file('mention_freq_48.html')
show(plot)
