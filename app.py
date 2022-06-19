from flask import Flask, request, redirect, render_template, url_for
from boto.s3.connection import S3Connection
from spotifyclient import SpotifyClient
from seatgeekclient import SeatGeekClient
import os

app = Flask(__name__)
app.secret_key = 'super secret key omg'

sp_client_id = S3Connection(os.environ['sp_client_id'])
sp_client_secret = S3Connection(os.environ['sp_client_secret'])

sp = SpotifyClient(sp_client_id, sp_client_secret)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/authorize')
def authorize():
    url = sp.get_auth_url()
    return redirect(url)

@app.route('/callback')
def callback():
    auth_token = request.args.get('code')
    sp.perform_auth(auth_token)
    playlist_ids = sp.get_user_playlists()
    if playlist_ids == 'error':
        return render_template('error.html')
    return render_template('playlists.html', playlist_info = playlist_ids)

@app.route('/selectedplaylist/<id>', defaults = {'city': None})
@app.route('/selectedplaylist/<id>/<city>')
def selected_playlist(id, city):
    playlist_songs = sp.playlist_songs(id)
    if playlist_songs == 'error':
        return render_template('error.html')
    artists = sp.get_artists(playlist_songs)
    sg_client_id = S3Connection(os.environ['sg_client_id'])
    sg_api_key = S3Connection(os.environ['sg_api_key'])
    sg = SeatGeekClient(sg_client_id, sg_api_key)
    concerts =  sg.get_events(artists, city)
    return render_template('concerts.html', concert_info = concerts)

@app.route('/selectedplaylist/<id>/<city1>/', defaults = {'city2': None})
@app.route('/selectedplaylist/<id>/<city1>/<city2>')
def selected_playlist_redirect(id, city1, city2):
    if city2 == None:
        return redirect('/selectedplaylist/' + id)
    return(redirect('/selectedplaylist/' + id + '/' + city2))

if __name__ == '__main__':
    app.run(threaded = True, port = 5000)