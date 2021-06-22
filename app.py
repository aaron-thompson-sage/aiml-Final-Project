import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import spotipy
import math
from spotipy.oauth2 import SpotifyClientCredentials
import os
#import psycopg2
from rq import Queue
from worker import conn
import sys

q = Queue(connection = conn)

########### Define your variables ######

myheading1='Song variety by Artist'
tabtitle = 'Final Project - Aaron Thompson'
sourceurl = 'https://github.com/aaron-thompson-sage/aiml-Final-Project/blob/main/Final%20Project.ipynb'
githublink = 'https://github.com/aaron-thompson-sage/aiml-Final-Project'
lastclickcount = 0
lastartistname = ''
tracks = []
clientid = 'a2b4005538904434809bf1a8974f3eb7'
clientsecret = 'ea77d14c398e41d394fdcf94c1c79347'
job = None
#DATABASE_URL = os.environ['DATABASE_URL']
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout

app.layout = html.Div(children=[
    html.H1(myheading1),
    html.Br(),
    html.Div(children=[dcc.Markdown('Enter an artist name')]),
    dcc.Input(id='artistname', value='', type='text'),
    html.Br(),
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
    html.Br(),
    html.Div(children=[dcc.Markdown('Max songs to search')]),
    dcc.Dropdown(id='maxsongs',
        options = [
            {'label': 'a few', 'value' : '20'},
            {'label': 'normal', 'value' : '200'},
            {'label': 'a lot', 'value' : '1500'}
        ],
        value = '20'),
    html.Br(),
    html.Button('Submit', id='button'),
    html.Div(id='my-div'),
    html.Br(),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A("Data Source", href=sourceurl),
    ]
)


def distance_feature(feature1, feature2, featurename):
    diff = feature1[featurename] - feature2[featurename]
    return diff*diff

def getdistance(f1, f2, features):
    distance = 0
    for feature in features:
        distance += distance_feature(f1, f2, feature)
    return math.sqrt(distance)

def findopposite(tracks, comparetrack, features):
    bestmatch = ''
    bestdistance = 1
    worstmatch = ''
    worstdistance = 0
    for track in tracks:
        if (track):
            distance = getdistance(comparetrack, track, features)
            if distance > 0 and comparetrack['name'] != track['name']:
                if distance < bestdistance:
                    bestmatch = track
                    bestdistance = distance
                if distance > worstdistance:
                    worstmatch = track
                    worstdistance = distance

    return worstmatch

def featureprint(track, features):
    output = ''
    for feature in features:
        output = output + feature[0] + '(' + str(track[feature]) + ')'
    return output

def load_tracks(artistname, maxsongs):
    global clientid
    global clientsecret

    client_credentials_manager = SpotifyClientCredentials(client_id=clientid, client_secret=clientsecret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=artistname, type='artist', limit=20, offset=0)

    artisturi = results['artists']['items'][0]['id']

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=clientid, client_secret=clientsecret))

    results = spotify.artist_albums(artisturi, album_type='album')
    allalbums = results['items']
    while results['next']:
        results = spotify.next(results)
        allalbums.extend(results['items'])

    albumtracks = []
    tids = []
    tracks = []
    albums = []
    for album in allalbums:
        addalbum = True
        for existingalbum in albums:
            if existingalbum['name'] == album['name']:
                addalbum = False
                break
        if addalbum:
            albums.append(album)

    print(albums[0]['artist'], file=sys.stdout)

    for album in albums:
        print(album['name'], file=sys.stdout)
        if len(tracks) > int(maxsongs):
            break;
        for track in spotify.album_tracks(album['id'])['items']:
            feature = sp.audio_features(track['id'])[0]
            feature['name'] = track['name']
            tracks.append(feature)
            if len(tracks) > int(maxsongs):
                break;
    return tracks

########## Define Callback
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='artistname', component_property='value'),
    Input(component_id='features', component_property='value'),
    Input(component_id='maxsongs', component_property='value'),
    Input(component_id='button', component_property='n_clicks')
    ]
)
def update_output_div(artistname, features, maxsongs, clicks):
    global lastclickcount
    global lastartistname
    global tracks
    global job

    if (clicks is None):
        return "Click Submit to make a new calculation."

    if (int(clicks) <= lastclickcount):
        return

    lastclickcount = int(clicks)

    if artistname != lastartistname:
        lastartistname = artistname

        tracks = load_tracks(artistname, maxsongs)
        #job = q.enqueue(load_tracks, artistname, maxsongs)

    #if job.result == None:
        #return "working... wait a bit longer and press Submit again."

    comparetrack = tracks[0]

    maxtrycount = 20
    opposite = findopposite(tracks, comparetrack, features)
    doubleopposite = findopposite(tracks, opposite, features)
    while comparetrack['name'] != doubleopposite['name'] and maxtrycount > 0:
        comparetrack = opposite
        opposite = findopposite(tracks, comparetrack, features)
        doubleopposite = findopposite(tracks, opposite, features)
        maxtrycount -= 1

    outstring = 'These 2 songs are opposites: ' + comparetrack['name'] + ' and ' + opposite['name'] + '.  '
    outstring = outstring + 'Feature values for ' + comparetrack['name'] + ': ' + featureprint(comparetrack, features)
    outstring = outstring + ', and for ' + opposite['name'] + ': ' + featureprint(opposite, features) + '.'

    return outstring


############ Deploy
if __name__ == '__main__':
    app.run_server()
