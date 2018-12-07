import dash
import dash_core_components as dcc
import dash_html_components as html
from fetch_price import fetch, get_tickers
import dash_table
from dash.dependencies import Input, Output

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
                        'https://fonts.googleapis.com/css?family=Montserrat:\
                         400,700']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = fetch('AAPL')
ticks = get_tickers()

app.layout = html.Div(children=[
    html.H1('Stock Price Display'),
    html.Label('Select Stock: '),
    dcc.Dropdown(
        id='example-dropdown',
        options=[{'label': r[2], 'value': r[0]} for r in ticks.values],
        value=['AAPL'],
        multi=True,
    ),
    dcc.Graph(
        id='example-graph',
        figure={
        }
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        # pagination_settings = {'page_size': 20, 'current_page': 0},
        style_cell={'textAlign': 'left', 'padding': '5px',
                    'font-family': 'Montserrat'},
        style_table={
            'maxHeight': '300px',
            'overflowY': 'scroll'
        }
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
        'data': [{'x': df[df.ticker == val].date, 'y':
                  df[df.ticker == val].adj_close, 'type': 'line', 'name': val}
                 for val in input_value]
    }
    return figure


@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='example-dropdown', component_property='value')]
)
def update_table(input_value):
    # time.sleep(1)
    ticker = ','.join(input_value)
    df = fetch(ticker)
    return df.to_dict("rows")


if __name__ == '__main__':
    app.run_server(debug=True)
