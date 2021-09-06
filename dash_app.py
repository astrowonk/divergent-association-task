from dash import Dash, Input, Output, State, html, dcc, dash_table, callback
import dash_bootstrap_components as dbc
import plotly.express as px

app = Dash('myapp',
           prevent_initial_callbacks=True,
           suppress_callback_exceptions=True)

input_div = html.Div(dcc.Input(id='words-input', type='text'))
score = html.H4(id='score')
graph = html.Div(id='graph')

from dat import Model
m = Model()

app.layout = dbc.Container([dbc.Row([input_div, score, graph])])


@app.callback(Output('score', 'children'), Output('graph', 'children'),
              Input('words-input', 'value'))
def update_score(words):
    print(words)
    if not words:
        return Dash.no_update
    score = m.dat(words.split(), minimum=2)
    fig = m.plot_words(words.split())
    return score, dcc.Graph(id='figure', figure=fig)


if __name__ == "__main__":

    app.run_server(debug=True)
