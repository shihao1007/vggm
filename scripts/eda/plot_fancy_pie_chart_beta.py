# -*- coding: utf-8 -*-
"""
Created on Wed May 15 21:32:21 2019

this script plots a VERY fancy pie plot
to visualize the language distribution within each community
The style is copied from Burtin's bacteria plot

@author: Shihao Ran
         STIM Laboratory
"""

# import packages
from collections import OrderedDict
from math import log, sqrt

import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
#%%
# specify colors for languages and games
lang_color = OrderedDict([
        # Blues7[2] for English
        ("English",     "Black"),
        # PuRd7[2] for Japanese
        ("Japanese",    "#08306b"),
        # Purples6[1] for French
        ("French",      "#b30000"),
        # Greens6[1] for Spanish
        ("Spanish",     "#225ea8")])

game_color = OrderedDict([
        ("Fortnite",        "#e69584"),
        ("ApexLegends",     "#e69584"),
        ("overwatch",       "#aeaeb8"),
        ("LeagueOfLegends", "#aeaeb8"),
        ("CSGO",            "#aeaeb8"),
        ("dota2",           "#e69584"),
        ("Hearthstone",     "#e69584"),
        ("GrandTheftAutoV", "#aeaeb8")])

# load the dataframes
df = pd.read_csv(r'./dataframes/langs.csv')
# extract only the top4 languages used
df_4langs = df[(df.lang=='en')|(df.lang=='ja')|(df.lang=='fr')|(df.lang=='es')]
# count the numbers for each game and each language
df_cnt = df_4langs.groupby(['game', 'lang']).count()
# unstack the multi-index after groupby
df_cnt = df_cnt.unstack(level=-1)
# unstack the multi-index column names
df_cnt.columns=df_cnt.columns.droplevel(0)
# move the game name from index to a column
df_cnt.reset_index(inplace=True)
#%%
# function that computes radius from count
def rad(mic):
    return a * np.log(mic) + b

#%%
# specify the plot size
# outter square
width = 800
height = 800
# inner circle
inner_radius = 90
# outter circle
outer_radius = 300 - 10

# set the parameters for scaling the counting bars
minr = np.log(1)
maxr = np.log(50000)
# slope of the linear scaling
a = (outer_radius - inner_radius) / (maxr - minr)
# make sure they are longer than inner radius
b = inner_radius

# compute the angles for all the annular_wedges
big_angle = 2.0 * np.pi / (len(df_cnt) + 1)
small_angle = big_angle / 9

# define the hover tool
hover = HoverTool(names=['en', 'es', 'fr', 'ja'],
                  tooltips='@game, @language: @count')

# initialize the plot
p = figure(plot_width=width, plot_height=height, title="",
    x_axis_type=None, y_axis_type=None,
    x_range=(-380, 380), y_range=(-380, 380),
    min_border=0, outline_line_color="black",
    background_fill_color="#f0e1d2",
    tools=[hover,], toolbar_location=None)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

# plot annular wedges
angles = np.pi/2 - big_angle/2 - df_cnt.index.to_series()*big_angle
colors = [game_color[game] for game in df_cnt.game]
p.annular_wedge(
    0, 0, inner_radius, outer_radius, -big_angle+angles, angles, color=colors,
)

# make additional dataframes for all the languages individually
df_en = df_cnt[['game', 'en']]
df_en.columns=['game', 'count']
df_en['language'] = 'English'

df_es = df_cnt[['game', 'es']]
df_es.columns=['game', 'count']
df_es['language'] = 'Spanish'

df_fr = df_cnt[['game', 'fr']]
df_fr.columns=['game', 'count']
df_fr['language'] = 'French'

df_ja = df_cnt[['game', 'ja']]
df_ja.columns=['game', 'count']
df_ja['language'] = 'Japanese'

# calcualte the outter radius for all the languages
df_en['out_rad_en'] = df_cnt.en.apply(rad)
df_es['out_rad_es'] = df_cnt.es.apply(rad)
df_fr['out_rad_fr'] = df_cnt.fr.apply(rad)
df_ja['out_rad_ja'] = df_cnt.ja.apply(rad)

# calculate the starting and ending angles for them
df_en['sa_en'] = -big_angle+angles+7*small_angle
df_es['sa_es'] = -big_angle+angles+5*small_angle
df_fr['sa_fr'] = -big_angle+angles+3*small_angle
df_ja['sa_ja'] = -big_angle+angles+1*small_angle

df_en['ea_en'] = -big_angle+angles+8*small_angle
df_es['ea_es'] = -big_angle+angles+6*small_angle
df_fr['ea_fr'] = -big_angle+angles+4*small_angle
df_ja['ea_ja'] = -big_angle+angles+2*small_angle

# make column data sources
source_en = ColumnDataSource(df_en)
source_es = ColumnDataSource(df_es)
source_fr = ColumnDataSource(df_fr)
source_ja = ColumnDataSource(df_ja)

# small wedges
p.annular_wedge(0, 0, inner_radius, 'out_rad_en', 'sa_en', 'ea_en',
                source=source_en, color=lang_color['English'], name='en')
p.annular_wedge(0, 0, inner_radius, 'out_rad_es', 'sa_es', 'ea_es',
                source=source_es, color=lang_color['Spanish'], name='es')
p.annular_wedge(0, 0, inner_radius, 'out_rad_fr', 'sa_fr', 'ea_fr',
                source=source_fr, color=lang_color['French'], name='fr')
p.annular_wedge(0, 0, inner_radius, 'out_rad_ja', 'sa_ja', 'ea_ja',
                source=source_ja, color=lang_color['Japanese'], name='ja')
#%%
# circular axes and lables
labels = [1, 100, 1000, 5000, 25000, 50000]
radii = (a * np.log(labels) + b)
p.circle(0, 0, radius=radii, fill_color=None, line_color="white")
p.text(0, radii, [str(r) for r in labels],
       text_font_size="8pt", text_align="center", text_baseline="middle")

# radial axes
p.annular_wedge(0, 0, inner_radius-10, outer_radius+10,
                -big_angle+angles, -big_angle+angles, color="black")

# game labels
xr = radii[-1]*np.cos(np.array(-big_angle/2 + angles))
yr = radii[-1]*np.sin(np.array(-big_angle/2 + angles))
label_angle=np.array(-big_angle/2+angles)
label_angle[label_angle < -np.pi/2] += np.pi
p.text(xr, yr, df_cnt.game, angle=label_angle,
       text_font_size="11pt", text_align="center", text_baseline="middle")

# display legeends for languages
p.rect([-40, -40, -40, -40], [30, 10, -10, -30], width=30, height=13,
       color=list(lang_color.values()))
p.text([-15, -15, -15, -15], [30, 10, -10, -30], text=list(lang_color),
       text_font_size="9pt", text_align="left", text_baseline="middle")

output_file("burtin.html", title="Gaming Community Languages")
show(p)
