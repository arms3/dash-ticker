import dash
import dash_core_components as dcc
import dash_html_components as html
from fetch_price import fetch, get_tickers
import dash_table
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = fetch()
ticks = get_tickers()

app.layout = html.Div(children=[
    html.H1('Stock Price Display'),
    html.Div([
        html.Label('Select Stock'),
        dcc.Dropdown(
            id='example-dropdown',
            options=[{'label':r, 'value':r} for r in ticks],
            value=['AAPL'],
            multi=True
        )
    ]),
    dcc.Graph(
        id='example-graph',
        figure={
        }
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
    ),
])


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    [Input(component_id='example-dropdown', component_property='value')]
)
def update_chart(input_value):
    ticker = ','.join(input_value)
    df = fetch(ticker)
    figure = {
        'data': [{'x':df[df.ticker == val].date, 'y':df[df.ticker == val].adj_close, 'type':'line', 'name':val} for val in input_value]
    }
    return figure

@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='example-dropdown', component_property='value')]
)
def update_chart(input_value):
    ticker = ','.join(input_value)
    df = fetch(ticker)
    return df.to_dict("rows")


if __name__ == '__main__':
    app.run_server(debug=True)
