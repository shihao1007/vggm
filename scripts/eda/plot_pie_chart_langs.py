# -*- coding: utf-8 -*-
"""
Created on Wed May 15 20:06:36 2019

create a pie chart for the top10 used languages

@author: Shihao Ran
         STIM Laboratory
"""

from math import pi
import numpy as np
import pandas as pd

from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum

# load the dataframe
df = pd.read_csv(r'./dataframes/langs.csv')

# take out game and langs column from the dataframe
# and count the number for languages by using groupby
langs_count = df[['game', 'lang']].groupby('lang').count()
langs = list(langs_count.index)
counts = langs_count.game.tolist()

# scale the value by log function
#langs=np.log10(langs)
#counts=np.log10(counts)

# sort the names and counts
sorted_langs = sorted(langs, key=lambda x: -counts[langs.index(x)])[:10]
sorted_counts = sorted(counts, reverse=True)[:10]
#%%
# make a dictionary with the name:count pair
x={lang: count for lang, count in zip(sorted_langs, sorted_counts)}

# add addtional information for plotting
data = pd.Series(x).reset_index(name='value').rename(columns={'index':'Language'})
data['angle'] = data['value']/data['value'].sum() * 2*pi
data['color'] = Category20c[len(x)]
data['Percentage'] = round(data['value']/sum(counts), 4)*100

# initialize the plot
p = figure(plot_height=300, plot_width=380, title='Overall % of languages', toolbar_location=None,
           tools="hover", tooltips="@Language: @Percentage %", x_range=(-0.25, 0.38),
           y_range=(-0.3, 0.3))

# plot the pie
p.wedge(x=0, y=0, radius=0.23,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='Language', source=data)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None
p.legend.orientation = "vertical"
p.legend.location = "center_right"

output_file('10langs_pie.html')
show(p)
