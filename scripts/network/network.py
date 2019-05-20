# -*- coding: utf-8 -*-
"""
Created on Sun May 19 14:51:07 2019

this script visualize the network

@author: Shihao Ran
         STIM Laboratory
"""

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import show, output_file
from bokeh.models import Range1d, MultiLine, Circle
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges
from bokeh.palettes import Reds7, Blues4, YlOrRd4
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import row
#%%
# load the data frame
df = pd.read_csv(r'./dataframes/retweet_csgo.csv')
#%%
# convert the dataframe into a Networkx object
G_reply = nx.from_pandas_edgelist(df, 
                                  source='tweet_user_id',
                                  target='retweeted_user_id',
                                  create_using=nx.DiGraph())

# get the circle sizes from the degrees of the nodes
# a list for plot using networkx draw
sizes = [x[1]*10 for x in G_reply.degree()]

# a dictionary for plot using bokeh
node_sizes = {x[0]:min(x[1], 6)*4 for x in G_reply.degree()}

# set the node size attribution
nx.set_node_attributes(G_reply, node_sizes, 'node_size')

#%%
# plot using networkx draw network
#plt.figure()
#nx.draw_networkx(G_reply, node_size = sizes, 
#                with_labels = False, 
#                alpha = 0.3,
#                width = 0.3)
#plt.axis('off')
#%%
# plot using bokeh

# make a column data source for the nodes
nodes_df = pd.DataFrame.from_dict({k:v for k,v in G_reply.nodes(data=True)},
                                   orient='index')
source_nodes = ColumnDataSource(nodes_df)

# tools for linking plots
TOOLS = 'hover, box_select'

# plot the first figure
plot1 = figure(plot_width=500, plot_height=500,
               x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1),
               tools=TOOLS, tooltips=([('user id', '@index')]),
               toolbar_location=None)

plot1.title.text = "CSGO Retweet Network (Spring Layout)"

# convert the nerworkx object to a graph renderer
graph_renderer = from_networkx(G_reply, nx.spring_layout, center=(0,0))
# specify the source so the size of the circles are related to the degrees
graph_renderer.node_renderer.data_source = source_nodes
# render the nodes
# 1 render the normal state nodes
graph_renderer.node_renderer.glyph = Circle(size='node_size',
                                            fill_alpha=0.4,
                                            fill_color=Reds7[2],
                                            line_color=Reds7[2])
# 2 render the selected nodes
graph_renderer.node_renderer.selection_glyph = Circle(size='node_size',
                                                      fill_alpha=0.6,
                                                      fill_color=Blues4[0],
                                                      line_color=Blues4[0])
# 3 render the hovered nodes
graph_renderer.node_renderer.hover_glyph = Circle(size='node_size',
                                                  fill_alpha=0.6,
                                                  fill_color='#a8ddb5',
                                                  line_color='#a8ddb5')

# render the edges
# 1 render the normal edges
graph_renderer.edge_renderer.glyph = MultiLine(line_color="gray",
                                               line_alpha=0.6,
                                               line_width=1)
# 2 render the selected edges
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Blues4[0],
                                                         line_alpha=0.6,
                                                         line_width=1)
# 3 render the hovered edges
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=YlOrRd4[0],
                                                     line_alpha=0.6,
                                                     line_width=1)

# specify the heviour of selection and hovering
graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

# use the graph renderer to render plot 1
plot1.renderers.append(graph_renderer)

#%%
# similar workflow for the second plot

plot2 = figure(plot_width=500, plot_height=500,
            x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1),
            tools=TOOLS, tooltips=([('user id', '@index')]),
            toolbar_location=None)
plot2.title.text = "CSGO Retweet Network (Kamada-Kawai Layout)"

graph_renderer = from_networkx(G_reply, nx.kamada_kawai_layout, center=(0,0))
graph_renderer.node_renderer.data_source = source_nodes

graph_renderer.node_renderer.glyph = Circle(size='node_size',
                                            fill_alpha=0.4,
                                            fill_color=Reds7[2],
                                            line_color=Reds7[2])
graph_renderer.node_renderer.selection_glyph = Circle(size='node_size',
                                                      fill_alpha=0.6,
                                                      fill_color=Blues4[0],
                                                      line_color=Blues4[0])
graph_renderer.node_renderer.hover_glyph = Circle(size='node_size',
                                                  fill_alpha=0.6,
                                                  fill_color='#a8ddb5',
                                                  line_color='#a8ddb5')

graph_renderer.edge_renderer.glyph = MultiLine(line_color="gray",
                                               line_alpha=0.6,
                                               line_width=1)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Blues4[0],
                                                         line_alpha=0.6,
                                                         line_width=1)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=YlOrRd4[0],
                                                     line_alpha=0.6,
                                                     line_width=1)

graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

plot2.renderers.append(graph_renderer)

#%%
#output and show the plots
output_file("retweet_networkx_graph.html")
show(row(plot1, plot2))