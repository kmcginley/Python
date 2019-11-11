import dash
import io
import base64
import json

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go

import numpy as np
import scipy
from scipy import stats
import pandas as pd

from survival_plotly import *


app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H1('Dash Tabs component demo'),
    dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
        dcc.Tab(label='Leaf Disk', value='tab-1-example'),
        dcc.Tab(label='Survival', value='tab-2-example')]),
    #html.Div(id='tabs-content-example'),
    html.Div(id='error'),
    html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=True
                    )]),
    html.Div(id='p1'),
    html.Div(id='container', children = [
        dcc.Graph(id='g1', style={'display': 'none'})]),
    html.Div(id='container2', children=[
        dcc.Checklist(id='checklist', options=[
                    {'label': 'Plot 1', 'value': 'p1'},
                    {'label': 'Plot 2', 'value': 'p2'},
                    {'label': 'Plot 3', 'value': 'p3'}
                    ],
                    value=['p1'], style={'display': 'none'})
    ])
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    newdf = df

    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ]), newdf

# run t-test and draw line traces
def get_ttest(mydf, treatments):

    # get max Day7_area value to know where to start drawing line traces
    maxVal = mydf['Day7_area'].max()
    lowerLimit = maxVal+0
    upperLimit = maxVal+1
    data = []
    sig = ''
    treatments.pop(treatments.index('water-auto'))

    for i in treatments:
        if i[-3:]=='man':
            water = 'water-man'
            set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
            set2 = mydf[mydf['Agent_name']=='water-man']['Day7_area'].values
        elif i[-4:]=='auto':
            water = 'water-auto'
            set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
            set2 = mydf[mydf['Agent_name']=='water-auto']['Day7_area'].values
        else:
            water = 'water'
            set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
            set2 = mydf[mydf['Agent_name']=='water']['Day7_area'].values

        ttest = scipy.stats.ttest_ind(set1, set2)
        if ttest[1] > 0.05:
            sig = 'ns'
        elif ttest[1] <= 0.0001:
            sig = '****'
        elif ttest[1] <= 0.001:
            sig = '***'
        elif ttest[1] <= 0.01:
            sig = '**'
        elif ttest[1] <= 0.05:
            sig = '*'


        trace = go.Scatter(
            x=[i, i, water, water], 
            y=[lowerLimit, upperLimit, upperLimit, lowerLimit], 
            mode = 'lines+text', 
            text=['',sig], 
            showlegend=False)

        data.append(trace)
        lowerLimit += 3
        upperLimit += 3

    return data


# @app.callback([#Output('tabs-content-example', 'children'),
#                 Output('checklist', 'style')],
#               [Input('tabs-example', 'value')])
# def render_content(tab):
#     if tab == 'tab-1-example':

#         # return html.Div([
#         #             dcc.Upload(
#         #                 id='upload-data',
#         #                 children=html.Div([
#         #                     'Drag and Drop or ',
#         #                     html.A('Select Files')
#         #                 ]),
#         #                 style={
#         #                     'width': '100%',
#         #                     'height': '60px',
#         #                     'lineHeight': '60px',
#         #                     'borderWidth': '1px',
#         #                     'borderStyle': 'dashed',
#         #                     'borderRadius': '5px',
#         #                     'textAlign': 'center',
#         #                     'margin': '10px'
#         #                     },
#         #                     # Allow multiple files to be uploaded
#         #                     multiple=True
#         #             )]),
#         return ({'display': 'none'},)

#     elif tab == 'tab-2-example':

#         return html.Div([
#                 dcc.Upload(
#                     id='upload-data',
#                     children=html.Div([
#                         'Drag and Drop or ',
#                         html.A('Select Files')
#                     ]),
#                     style={
#                         'width': '100%',
#                         'height': '60px',
#                         'lineHeight': '60px',
#                         'borderWidth': '1px',
#                         'borderStyle': 'dashed',
#                         'borderRadius': '5px',
#                         'textAlign': 'center',
#                         'margin': '10px'
#         },
#         # Allow multiple files to be uploaded
#         multiple=True
#     )]), {'display': 'block'}

@app.callback([Output('g1', 'figure'),
            Output('g1', 'style'),
            Output('error', 'children'),
            Output('p1', 'children'),
            Output('checklist', 'style')],
              [Input('tabs-example', 'value'),
              Input('upload-data', 'contents'),
              Input('checklist', 'value')],
              [State('upload-data', 'filename')])

def update_output(tab, list_of_contents, value, list_of_names):
    #if list_of_contents is not None:

    # child,mydf = [
    #     parse_contents(c, n) for c, n in
    #     zip(list_of_contents, list_of_names)][0]
    
    if tab == 'tab-1-example':
        #array of unique treatments used to build the individual traces
        #if value == 'Distribution':
        if list_of_contents is not None:
            child,mydf = [
                parse_contents(c, n) for c, n in
                zip(list_of_contents, list_of_names)][0]
            try:
                if 'Method' in mydf.columns:
                    mydf['Method'] = [x.split('-')[1] for x in mydf.loc[:, 'Agent_name'].values]
                    mydf = mydf.sort_values('Method')
                else:
                    mydf = mydf.sort_values('Agent_name')

                treatments = [x for x in mydf['Agent_name'].unique()]
                
                data = []

                for i in treatments:
                    trace = go.Box(y=mydf[mydf['Agent_name']==i]['Day7_area'], name = i)
                    data.append(trace)

                data = data + get_ttest(mydf, treatments)

                # for every treatment, generate a line trace that connects it to the water control

                figure = go.Figure(data=data, layout={'height':800, 'clickmode':'event+select'})
                
                return figure, {'display': 'block'}, '', '', {'display':'none'}

            except:
                figure = go.Figure()
                return (figure, {'display':'none'}, "You've uploaded the wrong file type for the analysis chosen", '', {'display':'none'})
        else:
            figure = go.Figure()
            src = ''
            return (figure, {'display':'none'}, '', html.Img(src=src), {'display':'none'})
            #raise dash.exceptions.PreventUpdate

    elif tab == 'tab-2-example':

        figure = go.Figure()

        if list_of_contents is not None:
            
            child,mydf = [
                parse_contents(c, n) for c, n in
                zip(list_of_contents, list_of_names)][0]

            try:
                images = []
                if 'p1' in value:
                    images.append(plot1(mydf))
                if 'p2' in value:
                    images.append(plot2(mydf))
                if 'p3' in value:
                    images.append(plot3(mydf))
                    
                return (figure, {'display':'none'}, '', [html.Img(images[i]) for i in images], {'display':'none'})
                #return (figure, {'display':'none'}, '', [html.Img(src=src), html.Img(src=src2)], {'display':'none'})
            except:

                figure = go.Figure()
                return (figure, {'display':'none'}, "You've uploaded the wrong file type for the analysis chosen", '', {'display':'none'})

        else:
            print(6)
            src = ''
            return (figure, {'display':'none'}, '', html.Img(src=src), {'display':'block'})
            
            #raise dash.exceptions.PreventUpdate


            #     return (figure, {'display':'none'}, '', html.Img(src=src), {'display':'none'})
            # except:
                
            #     return (figure, {'display':'none'}, "You've uploaded the wrong file type for the analysis chosen", '', {'display':'block'})

    else:
        raise dash.exceptions.PreventUpdate

            



# @app.callback([Output('p1', 'children')],
#             [Input('upload-data', 'contents'),
#             Input('checklist', 'value')],
#             [State('upload-data', 'filename')]
# )

# def update_output(list_of_contents, value, list_of_names):
#     if list_of_contents is not None:
        
#         child, mydf = [
#             parse_contents(c, n) for c, n in
#             zip(list_of_contents, list_of_names)][0]
        
#         #array of unique treatments used to build the individual traces
#         #if value == 'Distribution':

#         try:
#             src = plot1(mydf)
#             #print(mydf)
#             return (html.Img(src=src),)
            
            
#         #     if 'Method' in mydf.columns:
#         #         mydf['Method'] = [x.split('-')[1] for x in mydf.loc[:, 'Agent_name'].values]
#         #         mydf = mydf.sort_values('Method')
#         #     else:
#         #         mydf = mydf.sort_values('Agent_name')

#         #     treatments = [x for x in mydf['Agent_name'].unique()]
            
#         #     data = []

#         #     for i in treatments:
#         #         trace = go.Box(y=mydf[mydf['Agent_name']==i]['Day7_area'], name = i)
#         #         data.append(trace)

#         #     data = data + get_ttest(mydf, treatments)

#         #     # for every treatment, generate a line trace that connects it to the water control

#         #     figure = go.Figure(data=data, layout={'height':800, 'clickmode':'event+select'})

#         #     return figure, {'display': 'block'}

#         except:

#             return ("You've uploaded the wrong file type for the analysis chosen",)

if __name__ == '__main__':
    app.run_server(debug=True)