import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from fetch_price import fetch, get_tickers
import dash_table
from dash.dependencies import Input, Output
import os
from random import randint
import pandas as pd

external_stylesheets = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css?family=Montserrat:400,700']

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server,
                external_stylesheets=external_stylesheets)
df = fetch('AAPL')
ticks = get_tickers()

app.layout = html.Div([

    # Navbar
    html.Nav(children=[
        html.Div([
            html.Div(html.A('Home', className='navbar-brand', href='/'), className='navbar-header'),
            html.Div(html.Ul(html.Li(html.A('About', href='/about')), className='nav navbar-nav navbar-right')),
        ], className='container')
    ], className="navbar navbar-inverse navbar-static-top"),

    # Main container
    html.Div([
        # Stock selector dropdown
        html.H1('Stock Price Explorer'),
        dcc.Dropdown(
            id='example-dropdown',
            options=[{'label': r[2], 'value': r[0]} for r in ticks.values],
            value=['AAPL'],
            multi=True,
        ),

        # Chart
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [{'x': df.date, 'y': df.adj_close, 'type': 'line', 'name': 'AAPL'}]
            }
        ),

        # Detailed table for selected stocks
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("rows"),
            # pagination_settings = {'page_size': 20, 'current_page': 0},
            style_cell={'textAlign': 'left', 'padding': '5px',
                        'font-family': 'Montserrat'},
            style_table={
                'maxHeight': '300px',
                'overflowY': 'scroll',
            }
        ),

        # Hidden div inside the app that stores the intermediate data
        html.Div(id='intermediate-value', style={'display': 'none'}),
    ], className="container"),
])


@app.callback(
    Output('intermediate-value', 'children'),
    [Input(component_id='example-dropdown', component_property='value')]
)
def fetch_intermediate(value):
    # single fetch call for both table and chart
    if value == '':
        return
    ticker = ','.join(value)
    df = fetch(ticker)
    if df is None:
        return
    else:
        return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    [Input(component_id='intermediate-value', component_property='children')]
)
def update_chart(input_value):
    if input_value is None:
        return
    df = pd.read_json(input_value, orient='split')
    tickers = list(df.ticker.unique())
    if df is None:
        return
    else:
        figure = {
            'data': [{'x': df[df.ticker == val].date, 'y':
                      df[df.ticker == val].adj_close, 'type': 'line', 'name':
                      val} for val in tickers]
        }
        return figure


@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='intermediate-value', component_property='children')]
)
def update_table(input_value):
    if input_value is None:
        return
    df = pd.read_json(input_value, orient='split')
    if df is None:
        return
    else:
        return df.to_dict("rows")


if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
