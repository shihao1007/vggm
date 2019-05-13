# -*- coding: utf-8 -*-
"""
Created on Tue May  7 18:20:18 2019

this script creates a pie plot for the game distribution

@author: Shihao Ran
         STIM Laboratory
"""

from math import pi
import numpy as np
import pandas as pd

from bokeh.io import output_file, show
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.transform import cumsum

hashtags = pd.read_csv(r'E:\self_learning\vggm\dataframes\hashtags.csv')

games = {'LeagueOfLegends': 0,
         'Fortnite': 0,
         'ApexLegends': 0,
         'Hearthstone':0}

for game, cnt in games.items():
    games[game] = np.sum(hashtags['text'].str.contains(game, case=False))

#output_file(r"C:\Users\demon\Dropbox\shihao-selfLearning\vggm\figures\pieGame.html")

x = games

data = pd.Series(x).reset_index(name='value').rename(columns={'index':'Game'})
data['angle'] = data['value']/data['value'].sum() * 2*pi
data['color'] = Category10[len(x)]
data['Percentage'] = round(data['value']/hashtags.count()[0], 4)*100

p = figure(plot_height=200, title='Overall % of Hashtags', toolbar_location=None,
           tools="hover", tooltips="@Game: @Percentage %", x_range=(-0.5, 1.0))

p.wedge(x=0, y=1, radius=0.2,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='Game', source=data)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

output_file('4games_pan.html')
show(p)