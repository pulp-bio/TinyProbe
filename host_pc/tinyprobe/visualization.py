"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich
        Sergei Vostrikov, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import plotly.graph_objects as go
import numpy as np
from plotly import tools
from plotly.graph_objs import Layout, YAxis, Scatter, Annotation, Annotations, Data, Figure, Marker, Font

def plot_channels(rf_data, f_sampling, channels_list):

    time = np.arange(0, rf_data.shape[0])/f_sampling

    step = 1. / len(channels_list)
    kwargs = dict(domain=[0, 0 + step], showticklabels=False, zeroline=False, showgrid=False)

    # create objects for layout and traces
    layout = Layout(yaxis=YAxis(kwargs), showlegend=False)
    traces = [Scatter(x=time, y=rf_data[:, channels_list[0]])]

    # loop over the channels
    for ii in range(1,len(channels_list)):
            kwargs.update(domain=[0 + ii * step, 0 + (ii + 1) * step])
            layout.update({'yaxis%d' % (ii + 1): YAxis(kwargs), 'showlegend': False})
            traces.append(Scatter(x=time, y=rf_data[:, channels_list[ii]], yaxis='y%d' % (ii + 1)))

    # add channel names using Annotations
    annotations = Annotations([Annotation(x=-0.06, y=0, xref='paper', yref='y%d' % (ii + 1),
                                          text=ch_name, 
                                          font=Font(size=12), 
                                          showarrow=False)
                              for ii, ch_name in enumerate(["Ch. " + str(i) for i in channels_list])])
    layout.update(annotations=annotations)

    # set the size of the figure and plot it
    layout.update(autosize=False, width=1000, height=1000)
    fig = Figure(data=Data(traces), layout=layout)
    fig.show()



def plot_trace(data, channel_number, f_sampling):
    
    time = np.arange(0, data.shape[0])/f_sampling
    value = data[:, channel_number]
    
    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=value,
                        mode='lines+markers',
                        name='lines'))
    
    # Edit the layout
    fig.update_layout(title='Data from channel ' + str(channel_number),
                      xaxis_title='Time',
                      yaxis_title='Signal')

    fig.show()
    
    return