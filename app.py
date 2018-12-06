import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(children=[
    html.H1('Hello World'),
    html.Div([
        '''
            Dash: web application framework.
            ''',
        html.Label('Select Stock'),
        dcc.Dropdown(
            options=[
                {'label': 'Apple', 'value': 'AAPL'},
                {'label': 'Microsoft', 'value': 'MSFT'},
                {'label': 'Google', 'value': 'GOOG'}
            ],
            value=['AAPL'],
            multi=True
        )
    ]),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y':[4, 1, 2], 'type':'line', 'name':'Apple'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Microsoft'},
            ]
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
