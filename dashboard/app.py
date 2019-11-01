import dash
import io
import base64

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go

import seaborn as sns, matplotlib.pyplot as plt
from statannot import add_stat_annotation
from test import *
import numpy as np
import scipy
from scipy import stats
import pandas as pd

app = dash.Dash(__name__)

app.layout = html.Div([
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
    ),
    dcc.RadioItems(id='radio',
        options=[
           # {'label': 'Distribution', 'value': 'Distribution'},
           # {'label': 'T-Test', 'value': 'ttest'}
        ],
        value = 'Distribution'
    ),
    html.Div([
    dcc.Graph(
        id='g1')], style={'height':'100%', 'width':'100%'})

    # html.Div([html.Img(id='p1', src='')],
    #     id='plot_div'),

    # html.Div(id='output-data-upload')
])

# modify input csv and save as dataframe
def leafDisk(df):
    # signal = difference between two means |x1 - x2|/(sqrt(sd1^2/num + sd2^2/num))
    # noise = variability of groups themselves

    #df = df[['Agent_name', 'Replicate_number', 'Wells', 'Day7_area', 'Control']]
    df = df.loc[:,('Agent_name', 'Replicate_number', 'Wells', 'Day7_area', 'Control')]
    
    new = df['Agent_name'].str.split('-', expand=True)

    df['Method']=new[1]
    df['Agent_name']=new[0]

    # get mean for each treatment
    df1 = df.groupby(['Method','Agent_name'], as_index=False).agg({'Day7_area': 'mean'})
    df1.rename({'Day7_area':'mean'}, inplace=True, axis=1)
    df = pd.merge(df, df1, how='left', on=['Agent_name', 'Method'])

    # get standard deviation for each treatment
    df2 = df.groupby(['Method','Agent_name'], as_index=False).agg({'Day7_area': 'std'})
    df2.rename({'Day7_area':'std'}, inplace=True, axis=1)
    df = pd.merge(df, df2, how='left', on=['Agent_name', 'Method'])

    # get number of samples for each treatment
    df3= df.groupby(['Method','Agent_name'], as_index=False).agg({'Day7_area': 'count'})
    df3.rename({'Day7_area':'count'}, inplace=True, axis=1)
    df = pd.merge(df, df3, how='left', on=['Agent_name', 'Method'])

    newdf = df.drop_duplicates(['Agent_name', 'Method'])

    return df, newdf



# get rows from input csv
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    #dfTtest = leafDisk(df)[0]
    newdf = df

    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ]), newdf#, dfTtest

@app.callback([#Output('output-data-upload', 'children'),
    Output('g1', 'figure'),
    #Output('p1', 'src')
    ],
    [Input('upload-data', 'contents'),
    Input('radio', 'value'),
    Input('g1', 'selectedData')],
    [State('upload-data', 'filename')])

def update_output(list_of_contents, value, click, list_of_names):
    

    if list_of_contents is not None:
        print(click)
        children, mydf = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)][0]
        
        #array of unique treatments used to build the individual traces
        if value == 'Distribution':
            if 'Method' in mydf.columns:
                mydf['Method'] = [x.split('-')[1] for x in mydf.loc[:, 'Agent_name'].values]
                mydf = mydf.sort_values('Method')
            else:
                mydf = mydf.sort_values('Agent_name')

            treatments = [x for x in mydf['Agent_name'].unique()]
            
            print(treatments)
            data = []
            x = 1
            for i in treatments:
                trace = go.Box(y=mydf[mydf['Agent_name']==i]['Day7_area'], name = i)
                data.append(trace)
                x += 1
            # get max Day7_area value to know where to start drawing line traces
            maxVal = mydf['Day7_area'].max()
            lowerLimit = maxVal+5
            upperLimit = maxVal+7
            sig = ''
            treatments.pop(treatments.index('water-auto'))
            for i in treatments:
                if i[-3:]=='man':
                    set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
                    set2 = mydf[mydf['Agent_name']=='water-man']['Day7_area'].values
                    ttest = scipy.stats.ttest_ind(set1, set2)
                    if ttest[1] > 0.05:
                        sig = 'ns'
                    if ttest[1] <= 0.05:
                        sig = '*'
                    if ttest[1] <= 0.01:
                        sig = '**'
                    if test[1] <= 0.001:
                        sig = '***'
                    if 0.00001 <= 0.0001:
                        sig = '****'

                    trace = go.Scatter(x=[i, i,'water-man',  'water-man'], y=[lowerLimit,upperLimit, upperLimit, lowerLimit], mode = 'lines+text', text=['',sig], showlegend=False)
                    data.append(trace)
                    lowerLimit += 10
                    upperLimit += 10

                elif i[-4:]=='auto':
                    set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
                    set2 = mydf[mydf['Agent_name']=='water-auto']['Day7_area'].values
                    ttest = scipy.stats.ttest_ind(set1, set2)
                    print(float(ttest[1]))
                    print(ttest[1] < 0.00001)
                    print(ttest[1] < 1)
                    if ttest[1] > 0.05:
                        sig = 'ns'
                    if ttest[1] <= 0.05:
                        sig = '*'
                    if ttest[1] <= 0.01:
                        sig = '**'
                    if ttest[1] <= 0.001:
                        sig = '***'
                    if ttest[1] <= 0.0001:
                        sig = '****'
                    print(sig)
                    trace = go.Scatter(x=[i, i, 'water-auto',  'water-auto'], y=[lowerLimit,upperLimit, upperLimit, lowerLimit], mode = 'lines+text', text=['',sig], showlegend=False)
                    data.append(trace)
                    lowerLimit += 10
                    upperLimit += 10
                
                else:
                    set1 = mydf[mydf['Agent_name']==i]['Day7_area'].values
                    set2 = mydf[mydf['Agent_name']=='water']['Day7_area'].values
                    ttest = scipy.stats.ttest_ind(set1, set2)
                    if ttest[1] > 0.05:
                        sig = 'ns'
                    if ttest[1] <= 0.05:
                        sig = '*'
                    if ttest[1] <= 0.01:
                        sig = '**'
                    if test[1] <= 0.001:
                        sig = '***'
                    if 0.00001 <= 0.0001:
                        sig = '****'
                    trace = go.Scatter(x=[i, i, 'water',  'water'], y=[lowerLimit,upperLimit, upperLimit, lowerLimit], mode = 'lines+text', text=['',sig], showlegend=False)
                    data.append(trace)
                    lowerLimit += 10
                    upperLimit += 10
                
# for every treatment, generate a line trace that connects it to the water control

            figure = go.Figure(data=data, layout={'clickmode':'event+select'})
            #src = ''

            #return children, figure
            return (figure,)

    else:

        raise dash.exceptions.PreventUpdate



if __name__ == "__main__":
    app.run_server(debug=True)