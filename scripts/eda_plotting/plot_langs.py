# -*- coding: utf-8 -*-
"""
Created on Wed May 15 19:13:13 2019

this script plot the language distribution

@author: Shihao Ran
         STIM Laboratory
"""

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.palettes import Category20c
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap

import pandas as pd
import numpy as np

#%%
df = pd.read_csv(r'./dataframes/langs.csv')
#%%
langs_count = df[['game', 'lang']].groupby('lang').count()
#%%
langs = list(langs_count.index)
counts = langs_count.game.tolist()

#langs=np.log10(langs)
counts=np.log10(counts)

sorted_langs = sorted(langs, key=lambda x: -counts[langs.index(x)])[:20]
sorted_counts = sorted(counts, reverse=True)[:20]
#%%
source = ColumnDataSource(data=dict(langs=sorted_langs, counts=sorted_counts))

p = figure(x_range=sorted_langs, plot_height=300, toolbar_location=None,
           tools='hover', tooltips=('@langs: @counts'),
           title="Language Counts")
p.vbar(x='langs', top='counts', width=0.5, line_color='white', source=source,
       fill_color=factor_cmap('langs', palette=Category20c[20], factors=sorted_langs))

p.xgrid.grid_line_color = None
#p.legend.orientation = "horizontal"
#p.legend.location = "top_center"
output_file("20langs_bar_chart.html")
show(p)