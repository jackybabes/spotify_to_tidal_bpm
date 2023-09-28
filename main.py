import os
import sys
import spotipy
import logging
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
from mutagen.easyid3 import EasyID3
import shutil

cwd = os.getcwd()
os.chdir(cwd + '/songs_output')
print(os.getcwd())



def download_song(spotdl, spotify_track, spotify_audio_features):
    url = spotify_track['external_urls']['spotify']
        
    songs = spotdl.search([url])

    for song in songs:
        song_info, path = spotdl.download(song)
        
        if 'tempo' in spotify_audio_features:
            metadata = EasyID3(path)
            metadata['bpm'] = str(int(spotify_audio_features['tempo']))
            metadata.save()
        
        # shutil.move(path, './songs_output/' + str(path))
        



def main():

    playlist_url = 'https://open.spotify.com/playlist/514FdL7PaCgkuaWg4tbBX9?si=1469bbcc1c964fa8'

    spotify_session = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    spotdl = Spotdl(client_id=os.getenv('SPOTIPY_CLIENT_ID'), client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'))

    try:
        spotify_playlist = spotify_session.playlist(playlist_url)
    except Exception as e:
        logging.error("Could not parse URL")
        logging.error(e)
        sys.exit(0)


    while spotify_playlist:
        for item in spotify_playlist['tracks']['items']:
            spotify_track = item['track']    
            logging.info(f"{spotify_track['artists'][0]['name']} – {spotify_track['name']}")
            spotify_audio_features = spotify_session.audio_features([spotify_track['uri']])[0]

            # TODO?
            # album_details = spotify_session.album(spotify_track['album']['uri'])
            # genres = album_details['genres']

            download_song(spotdl, spotify_track, spotify_audio_features)

        if 'next' in spotify_playlist:
            spotify_playlist = spotify_session.next(spotify_playlist)
        else:
            spotify_playlist = None

if __name__ == "__main__":
    logging.basicConfig(
        level = os.environ.get('LOGLEVEL', 'INFO').upper(),
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.StreamHandler()
        ]
    )
    main()
    logging.info("Fin")