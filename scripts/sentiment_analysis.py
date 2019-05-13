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
from bokeh.models import ColumnDataSource

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
games = ['LeagueOfLegends',
         'Fortnite',
         'ApexLegends',
         'Hearthstone']
#%%
for game in games:
    senti_lst = [sentiment[tweets.hashtag.str.contains(game, case=False)].resample('1 h').mean() for game in games]
#%%
for idx, (senti, name) in enumerate(zip(senti_lst, games)):
     senti_lst[idx]= senti.rename(name)
#%%
plot = figure(plot_height=250, plot_width=600,
              title='Sentiment Score',
              tools='pan, box_zoom, reset, hover',
              tooltips=[('sentiment score', '@score')])

for index, item in enumerate(senti_lst):
    source = ColumnDataSource(data={'hours': item.index.hour[:-3],
                                    'score': item[:-3]})
    plot.line(x='hours', y='score', source=source, legend=item.name, color=Category10[4][index])
    
plot.legend.location='bottom_left'

output_file('sentiment_score.html')
show(plot)