import os
import sys
import spotipy
import logging
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
from mutagen.easyid3 import EasyID3

DRIVE_PATH = 'E:\\'

os.chdir(DRIVE_PATH)

def download_songs(spotdl, tracks):

    urls = [track['url'] for track in tracks]
    searched_songs = spotdl.search(urls)

    for track in tracks:
        for song_tuple in searched_songs:
            if track['url'] == song_tuple.url:
                track['song'] = song_tuple
                break

    songs_to_download = [track['song'] for track in tracks if 'song' in track]

    songs_downloaded = spotdl.download_songs(songs_to_download)

    for track in tracks:
        for song_tuple in songs_downloaded:
            if track['url'] == song_tuple[0].url:
                track['path'] = DRIVE_PATH + str(song_tuple[1])
                break
    
def add_tempo_to_metadata(tracks):
    tracks_to_change = [track for track in tracks if 'song' in track]
    for track in tracks_to_change:
        audio_features = track['spotify_audio_features']
        track_path = track['path']
        if 'tempo' in audio_features:
            try:
                metadata = EasyID3(track_path)
                metadata['bpm'] = str(int(audio_features['tempo']))
                metadata.save()
            except Exception as e:
                print('could not open track')
                print(e)


def download_song(spotdl, spotify_track, spotify_audio_features):
    url = spotify_track['external_urls']['spotify']
        
    songs = spotdl.search([url])

    for song in songs:
        song_info, path = spotdl.download(song)
        
        if 'tempo' in spotify_audio_features:
            metadata = EasyID3(path)
            metadata['bpm'] = str(int(spotify_audio_features['tempo']))
            metadata.save()
        
def get_playlist_from_spotify(spotify_session, playlist_url):

    try:
        spotify_playlist = spotify_session.playlist_tracks(playlist_url)
    except Exception as e:
        logging.error("Could not parse URL")
        logging.error(e)
        sys.exit(0)
    
    tracks = []
    while spotify_playlist:
        for item in spotify_playlist['items']:
            spotify_track = item['track']    
            logging.info(f"{spotify_track['artists'][0]['name']} – {spotify_track['name']}")
            spotify_audio_features = spotify_session.audio_features([spotify_track['uri']])[0]

            # TODO
            # album_details = spotify_session.album(spotify_track['album']['uri'])
            # genres = album_details['genres']

            track = {}
            track['spotify_track'] = spotify_track
            track['spotify_audio_features'] = spotify_audio_features
            track['url'] = spotify_track['external_urls']['spotify']

            tracks.append(track)

        if 'next' in spotify_playlist:
            spotify_playlist = spotify_session.next(spotify_playlist)
        else:
            spotify_playlist = None

    return tracks

def main():

    usb_playlist = 'https://open.spotify.com/playlist/2LWpAnlvLEjt119BeGW0LI?si=5b39ad1d6d094ae9'

    spotify_session = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    spotdl = Spotdl(client_id=os.getenv('SPOTIPY_CLIENT_ID'), client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'))

    tracks = get_playlist_from_spotify(spotify_session, usb_playlist)

    logging.info(f'{len(tracks)} tracks in playlist')

    # Download Songs

    download_songs(spotdl, tracks)

    # Label Songs

    add_tempo_to_metadata(tracks)

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