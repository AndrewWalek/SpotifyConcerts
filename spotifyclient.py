import base64
import datetime
import requests
import logging
import os

class SpotifyClient():
    access_token = None
    access_token_expires = datetime.datetime.now()
    client_id = None
    client_secret = None
    refresh_token = None
    auth_header = None
    sp_redirect_uri = os.environ['sp_redirect_uri']
    redirect_uri = sp_redirect_uri
    token_url = 'https://accounts.spotify.com/api/token'
    auth_url = 'https://accounts.spotify.com/authorize?'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        creds_decoded = self.get_header_auth()
        self.auth_header =  {
            'Authorization': f'Basic {creds_decoded}',
            'Content_type': 'application/x-www-form-urlencoded'
        }

    def get_header_auth(self):
        client_creds = f'{self.client_id}:{self.client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_data(self, auth_token):
        return {
            'grant_type': 'authorization_code',
            'code': auth_token,
            'redirect_uri': self.redirect_uri
        }
    
    def check_refresh(self):
        if datetime.datetime.now() > self.access_token_expires:
            self.refresh()

    def refresh(self):
        if self.access_token == None:
            return False
        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        creds_decoded = self.get_header_auth()
        refresh_head = {
            'Authorization': f'Basic {creds_decoded}',
            'Content_type': 'application/x-www-form-urlencoded'
        }
        refresh_request = requests.post(self.token_url, headers = refresh_head, data = refresh_data)
        body = refresh_request.json()
        self.access_token = body['access_token']
        expires_in = body['expires_in']
        expires = datetime.datetime.now() + datetime.timedelta(seconds = expires_in)
        self.access_token_expires = expires
        return True

    def get_auth_url(self):
        url = self.auth_url
        url += 'client_id=' + self.client_id
        url += '&response_type=code'
        url += '&redirect_uri=' + self.redirect_uri
        url += '&show_dialog=true'
        return url

    def perform_auth(self, auth_token):
        token_data = self.get_token_data(auth_token)
        token_header = self.auth_header
        request = requests.post(self.token_url, headers = token_header, data = token_data, json = {'key': 'value'})
        if request.status_code not in range(200, 299):
            logging.error('perform_auth:' + str(request.status_code))
            return None
        data = request.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        expires_in = data['expires_in']
        expires = datetime.datetime.now() + datetime.timedelta(seconds = expires_in)
        self.access_token_expires = expires

    def get_user_playlists(self):
        if self.access_token == None:
            return 'error'
        self.check_refresh()
        header = {
            'Authorization': ('Bearer ' + self.access_token),
            'Content-Type': 'application/json'
        }
        playlist_request = requests.post('http://api.spotify.com/v1/me/playlists', headers = header)
        if playlist_request.status_code not in range(200, 299):
            logging.error('get_user_playlists:' + str(playlist_request.status_code))
            return None
        playlist_data = playlist_request.json()
        return playlist_data['items']

    def playlist_songs(self, playlist_id):
        if self.access_token == None:
            return 'error'
        self.check_refresh()
        header = {
            'Authorization': ('Bearer ' + self.access_token),
            'Content-Type': 'application/json'
        }
        post_url = 'http://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
        get_songs = requests.post(post_url, headers = header)
        if get_songs.status_code not in range(200, 299):
            logging.error('playlist_songs:' + str(get_songs.status_code))
            return None
        songs_data = get_songs.json()
        return songs_data['items']

    # Returns set of all artists in playlist
    def get_artists(self, songs):
        all_artists = set()
        for song_id in songs:
            for artist in song_id['track']['artists']:
                all_artists.add(artist['name'])
        return all_artists