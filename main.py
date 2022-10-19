import os
import sys
import spotipy
import tidalapi
import logging
import argparse
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

def tidal_login():
    pass

def spotify_login():
    pass

def process_song():
    pass

def get_tidal_playlists(session):
    tidal_playlists = session.user.playlists()
    tidal_playlists = [playlist for playlist in tidal_playlists if 'Auto Generated Playlist' in playlist.description]
    tidal_playlists_to_be_created = [tempo for tempo in range(70,185,5) if str(tempo) not in [playlist.name for playlist in tidal_playlists]]
    tidal_playlists += [session.user.create_playlist(f"{tempo}", f"Auto Generated Playlist - {tempo}BPM") for tempo in tidal_playlists_to_be_created]
    return tidal_playlists

def main():
    parser = argparse.ArgumentParser(description='Move Spotify songs to Tidal Playlists')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--url', help='Playlist URL to be moved')
    group.add_argument('-ls', '--liked-songs', action='store_true' ,help='Liked songs to be moved')
    args = parser.parse_args()
    if args.url:
        spotify_session = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
        try:
            spotify_playlist = spotify_session.playlist(args.url)
        except Exception as e:
            logging.error("Could not parse URL")
            logging.error(e)
            sys.exit(0)
    elif args.liked_songs:
        spotify_login_scope = "user-library-read"
        spotify_session = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=spotify_login_scope))
        spotify_playlist = spotify_session.current_user_saved_tracks()
    else:
        parser.print_help()
        sys.exit(0)

    tidal_session = tidalapi.Session()
    # # Will run until you visit the printed url and link your account
    # session.login_oauth_simple()
    # logging.info(session.check_login())
    token_type = 'Bearer'
    access_token = os.getenv('TIDAL_ACCESS_TOKEN')
    refresh_token = os.getenv('TIDAL_REFRESH_TOKEN')
    expiry_time = os.getenv('TIDAL_EXPIRY_TIME')
    tidal_session.load_oauth_session(token_type, access_token, refresh_token, expiry_time)

    tidal_playlists = get_tidal_playlists(tidal_session)

    while spotify_playlist:
        for item in spotify_playlist['items']:

            spotify_track = item['track']    
            logging.info(f"{spotify_track['artists'][0]['name']} – {spotify_track['name']}")

            spotify_audio_features = spotify_session.audio_features([spotify_track['uri']])[0]
            
            if isinstance(spotify_audio_features, type(None)):
                logging.warning("BPM Not Found")
                continue

            bpm_rounded = 5 * round(spotify_audio_features['tempo'] / 5)
            if bpm_rounded < 70 or bpm_rounded > 180:
                logging.warning("BPM too Low/High")
                continue

            tidal_search_result = tidal_session.search(
                query=f"{spotify_track['artists'][0]['name']} {spotify_track['name']}", 
                models=[tidalapi.media.Track]
            )
            if isinstance(tidal_search_result['top_hit'], type(None)):
                logging.warning("Track Not Found in Tidal")
                continue
            logging.info(f"{tidal_search_result['top_hit'].artist.name} - {tidal_search_result['top_hit'].name}")


            logging.info(f"Adding to playlist: {bpm_rounded}")
            tidal_target_playlist = [playlist for playlist in tidal_playlists if int(playlist.name) == bpm_rounded][0]
            tidal_target_playlist.add([tidal_search_result['top_hit'].id])
        
        if spotify_playlist['next']:
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
    # logging.info("Start Main")
    main()
    # logging.info("Fin")