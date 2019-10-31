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
            {'label': 'Distribution', 'value': 'Distribution'},
            {'label': 'T-Test', 'value': 'ttest'},
            {'label': 'Survival', 'value': 'survival'}
        ],
        value = 'Distribution'
    ),
    dcc.Graph(
        id='g1'),

    html.Div(id='output-data-upload')
])

# modify input csv and save as dataframe
def leafDisk(df):
    # signal = difference between two means |x1 - x2|/(sqrt(sd1^2/num + sd2^2/num))
    # noise = variability of groups themselves

    df = df[['Agent_name', 'Replicate_number', 'Wells', 'Day7_area', 'Control']]
    
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
    newdf = leafDisk(df)[0]


    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ]), newdf

@app.callback([Output('output-data-upload', 'children'),
    Output('g1', 'figure')],
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
            treatments = [x for x in mydf['Agent_name'].unique()]
            data = []
            x = 1
            for i in treatments:
                trace = go.Box(y=mydf[mydf['Agent_name']==i]['Day7_area'], name = i)
                data.append(trace)
                x += 1

            figure = go.Figure(data=data)

            return children, figure

    else:

        raise dash.exceptions.PreventUpdate



if __name__ == "__main__":
    app.run_server(debug=True)