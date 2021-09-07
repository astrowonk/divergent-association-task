from dash import Dash, Input, Output, State, html, dcc, callback, no_update
import dash_bootstrap_components as dbc

app = Dash('myapp', external_stylesheets=[dbc.themes.BOOTSTRAP])

input_div = html.Div(dcc.Input(
    id='words-input',
    type='text',
    placeholder='Enter words here, separated by spaces.',
    persistence=True,
    style={
        'width': '100%',
        'height': '60px',
        'font-size': '20px'
    }),
                     style={'width': '100%'})
score = html.H4(id='score')
graph = html.Div(id='graph', style={'width': '90%'})

from dat import Model
m = Model()
m.disable_minimum = True

app.layout = dbc.Container([
    dbc.Row([input_div]),
    dbc.Row(score),
    dbc.Row(graph),
])


@app.callback(Output('score', 'children'), Output('graph', 'children'),
              Input('words-input', 'value'))
def update_score(words):
    print(words)
    if not words:
        return no_update

    word_list = [m.validate(w) for w in words.split(' ') if m.validate(w)]
    if len(word_list) <= 1:
        return no_update
    score = m.dat(word_list)
    fig = m.plot_words(word_list)

    return f"Average Semantic Distance: {score.round(2)}", dcc.Graph(
        id='umap-figure',
        figure=fig,
        style={'height': '80vh'},
        config={'displayModeBar': False})


if __name__ == "__main__":

    app.run_server(debug=True)
