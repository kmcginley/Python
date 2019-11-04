import dash
import io
import base64

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

from survival_plotly import plot1

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


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
            {'label': 'Distribution', 'value': 'Distribution'},
            {'label': 'T-Test', 'value': 'ttest'}
        ],
        value = 'Distribution'
    ),
    html.Div(id = 'dynamic-controls')
    # dcc.Graph(id='g1'),

    # html.Img(id='p1', src='')

])

# get rows from input csv
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

@app.callback([#Output('output-data-upload', 'children'),
    # Output('g1', 'figure'),
    # Output('p1', 'src')
    Output('dynamic-controls', 'children')],
    [Input('upload-data', 'contents'),
    Input('radio', 'value')],
    [State('upload-data', 'filename')])

def update_output(list_of_contents, value, list_of_names):
    

    if list_of_contents is not None:

        children, mydf = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)][0]
        
        #array of unique treatments used to build the individual traces
        if value == 'Distribution':

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
            
                #return children, figure
                return (dcc.Graph(figure = figure),)
            except:
                return("You've uploaded the wrong file type for the analysis chosen",)

        elif value == 'ttest':

            figure = go.Figure()
            try:
                src = plot1(mydf)
                return (html.Img(src = src),)
            except:
                print('wrong file type')

                return ("You've uploaded the wrong file type for the analysis chosen",)
    else:

        raise dash.exceptions.PreventUpdate



if __name__ == "__main__":
    app.run_server(debug=True)