# -*- coding: utf-8 -*-
"""
Created on Wed May  8 20:46:32 2019

@author: Shihao Ran
         STIM Laboratory
"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool
import numpy as np

def set_time_index(df):
    """
    set the created_at column as the index
    """
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at')
    
    return df
#%%
sid = SentimentIntensityAnalyzer()
#%%
tweets = pd.read_csv(r'.\dataframes\tweets_text_with_hashtags_and_time.csv')
tweets = set_time_index(tweets)
sentiment_scores = tweets['text'].apply(sid.polarity_scores)
sentiment = sentiment_scores.apply(lambda x: x['compound'])
games = ['Fortnite',
         'ApexLegends',
         'overwatch',
         'LeagueOfLegends']
#%%
for game in games:
    senti_lst = [sentiment[tweets.text.str.contains(game, case=False)].resample('1 h').mean() for game in games]
#%%
for idx, (senti, name) in enumerate(zip(senti_lst, games)):
     senti_lst[idx]= senti.rename(name)
#%%
hover = HoverTool(
            tooltips=[
                    ('game', '@game'),
                    ('time', '@hours{%F:%r}'),
                    ('sentiment score', '@score{0.2f}'),
                    ],
            formatters={
                    'hours': 'datetime',
                    'frequency': 'printf',
                    },
            mode='mouse'
        )     

plot = figure(plot_height=400, plot_width=1000,
              title='Sentiment Score',
              tools=[hover],
              toolbar_location=None)

for index, item in enumerate(senti_lst):
    item_df = item.to_frame()
    item_df['game'] = item.name
    source = ColumnDataSource(data={'hours': pd.date_range(item.index[0], item.index[-1], len(item)),
                                    'score': item,
                                    'game': item_df['game']})
    plot.line(x='hours', y='score', source=source, legend=item.name,
              color=Category10[4][index], line_width=2)
    
plot.xaxis.formatter = DatetimeTickFormatter(days = ['%m-%d,%r'],
                                             hours = ['%m-%d,%r'],
                                             months = ['%m-%d,%r'])
plot.xaxis.major_label_orientation = -np.pi/4-np.pi/16
plot.xaxis[0].ticker.desired_num_ticks = 8
plot.legend.orientation = "horizontal"
plot.legend.location = "bottom_center"
output_file('sentiment_score_48.html')
show(plot)