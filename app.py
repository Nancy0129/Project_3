from dash import Dash, html, dcc
import plotly.express as pxr
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import redis
import json
import numpy as np
from dash.dependencies import Input, Output
r = redis.Redis(host='152.3.65.126', port=6379)
app = Dash(__name__)
app.y1=[]
app.y2=[]
app.y3=[]
metrics = r.get('xc139-proj3-output')
app.metrics = json.loads(metrics.decode("utf-8"))
app.layout = html.Div(
    html.Div([
        html.H4(children='Virtual Machine Resources Usage', 
        style={'textAlign': 'center','fontSize':'30px'}),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph1'),
        dcc.Graph(id='live-update-graph2'),
        dcc.Interval(
            id='interval-component',
            interval=5*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    
    metrics = r.get('xc139-proj3-output')
    app.metrics = json.loads(metrics.decode("utf-8"))
    
    
    return [html.Span(app.metrics['timestamp'], style={'padding': '5px', 'fontSize': '20px'}),html.Br() ,html.Br() ,
            html.Span('Average Memory Utilization over min: {} % '.format(str(app.metrics['avg-util-virtual_memory-60sec'])), 
            style={'padding': '5px', 'fontSize': '20px'})
            ]

@app.callback(Output('live-update-graph1', 'figure'),
              Input('interval-component', 'n_intervals'))
def time_series(n):
    time_range=36
    colors = ['rgb(255,0,0)','rgb(0,255,0)','rgb(255,0,255)','rgb(0,0,255)']
    app.y1.append([app.metrics[f'avg-util-cpu{i}-60sec'] for i in range(4)])
    app.y2.append([app.metrics[f'avg-util-cpu{i}-60min'] for i in range(4)])
    app.y3.append(app.metrics['avg-util-virtual_memory-60sec'])
    if len(app.y1)>time_range:
        app.y1.pop(0)
        app.y2.pop(0)
        app.y3.pop(0)
    
    fig = make_subplots(rows = 1, 
    cols = 3,
    subplot_titles=('CPU Utilization over min(%)','CPU Utilization over hour(%)','Memory Utilization over min(%)'))
    for i in range(4):
        fig.add_trace(go.Scatter(x=np.arange(len(app.y1))*5, y=np.array(app.y1)[:,i],name=f'CPU{i}_min',mode='lines',line={'color':colors[i]}) ,row=1,col=1)
        fig.add_trace(go.Scatter(x=np.arange(len(app.y2))*5, y=np.array(app.y2)[:,i],name=f'CPU{i}_h',line={'color':colors[i]}) ,row=1,col=2)
    fig.add_trace(go.Scatter(x=np.arange(len(app.y3))*5, y=np.array(app.y3),name='Memory',mode='lines',fill = 'tozeroy') ,row=1,col=3)
    fig.update_xaxes(title_text = 'Time (s)')
    fig.update_yaxes(title_text = 'Utilization (%)')
    fig.update_layout(
        width = 1500,
        height = 500
    )
    
    return fig


@app.callback(Output('live-update-graph2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    
    table_data = [['CPU ID', 'Avg Utilization over min(%)', 'Avg Utilization over hour(%)']]
    for i in range(4):
        table_data.append([str(i),app.metrics[f'avg-util-cpu{i}-60sec'],app.metrics[f'avg-util-cpu{i}-60min']])
    fig=ff.create_table(table_data, height_constant=60)
    tr1=go.Bar(x=[f'{i}' for i in range(4)],
    y=[app.metrics[f'avg-util-cpu{i}-60sec'] for i in range(4)],
    xaxis='x2', yaxis='y2',opacity=0.5,name='Over Min')
    tr2 =go.Bar(x=[f'{i}' for i in range(4)],
    y=[app.metrics[f'avg-util-cpu{i}-60min'] for i in range(4)],
    xaxis='x2', yaxis='y2',opacity=0.5,name='Over Hour')
    fig.add_traces([tr1, tr2])

    fig['layout']['xaxis2'] = {}
    fig['layout']['yaxis2'] = {}

    # Edit layout for subplots
    fig.layout.xaxis.update({'domain': [0, .5]})
    fig.layout.xaxis2.update({'domain': [0.6, 1.]})

    # The graph's yaxis MUST BE anchored to the graph's xaxis
    fig.layout.yaxis2.update({'anchor': 'x2'})
    fig.layout.yaxis2.update({'title': 'Avg Utilization (%)'})
    fig.layout.xaxis2.update({'title': 'CPU ID'})

    # Update the margins to add a title and see graph x-labels.
    fig.layout.margin.update({'t':50, 'b':100})

    fig.layout.update({'height':500})
    return fig
if __name__ == '__main__':
    app.run_server(debug=True,port=5101,host='0.0.0.0')
