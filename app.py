import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
from pages import new_trade, view_records


app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
    title='TradeMemo',
    update_title=None
)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content',)
])


@callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/new_trade':
        return new_trade.layout
    elif pathname in ['', '/', '/view_records']:
        return view_records.layout
    else:
        return html.H1('Ooops. 404')

if __name__ == '__main__':
    app.run_server(debug=False)
