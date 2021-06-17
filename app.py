import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

########### Define your variables ######

myheading1='Song variety by Artist'
tabtitle = 'Final Project - Aaron Thompson'
sourceurl = 'https://github.com/aaron-thompson-sage/'
githublink = 'https://github.com/aaron-thompson-sage/'

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout

app.layout = html.Div(children=[
    html.H1(myheading1),
    html.Div(children=[dcc.Markdown('Enter an artist name')]),
    dcc.Input(id='artistname', value='', type='text'),
    html.Div(children=[dcc.Markdown('Select features to compare')]),
    dcc.Checklist(id='features',
        options = [
            {'label': 'danceability', 'value': 'danceability'},
            {'label': 'energy', 'value': 'energy'},
            {'label': 'speechiness', 'value': 'speechiness'},
            {'label': 'acousticness', 'value': 'acousticness'},
            {'label': 'instrumentalness', 'value': 'instrumentalness'},
            {'label': 'liveness', 'value': 'liveness'},
            {'label': 'valence', 'value': 'valence'},
        ],
        value = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']),
    html.Div(children=[dcc.Markdown('Max songs to search')]),
    dcc.Dropdown(id='maxsongs',
        options = [
            {'label': 'a few', 'value' : '20'},
            {'label': 'normal', 'value' : '200'},
            {'label': 'a lot', 'value' : '1500'}
        ],
        value = '20'),
    html.Div(id='my-div'),
    html.Br(),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A("Data Source", href=sourceurl),
    ]
)


########## Define Callback
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='artistname', component_property='value'),
    Input(component_id='features', component_property='value'),
    Input(component_id='maxsongs', component_property='value'),
    ]
)
def update_output_div(artistname, features, maxsongs):
    outstring = 'Artist: ' + artistname + ', features: '
    for feature in features:
        outstring = outstring + feature + ' '
    outstring = outstring + 'max: ' + str(maxsongs)
    return outstring


############ Deploy
if __name__ == '__main__':
    app.run_server()
