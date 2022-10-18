import os
import spotipy
import tidalapi
import logging
from spotipy.oauth2 import SpotifyOAuth

spotify_login_scope = "user-library-read"
spotify_session = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=spotify_login_scope))

pl = spotify_session.playlist('https://open.spotify.com/playlist/7D9kZlQGt4aQoyYICPAGHK?si=7fc7696235dc4d8c')

print(pl)