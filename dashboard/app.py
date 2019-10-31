import dash
import io
import base64

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go

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
    dcc.Graph(
        id='g1'),

    html.Div(id='output-data-upload')
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ])

@app.callback([Output('output-data-upload', 'children'),
    Output('g1', 'figure')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    traces = [go.Scatter(
        x=[1,2,3,4],
        y=[10,20,30,40],
        mode='markers'
    )]
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        
        figure = go.Figure(data=traces)
        return children, figure

    else:

        raise dash.exceptions.PreventUpdate



if __name__ == "__main__":
    app.run_server(debug=True)