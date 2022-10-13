import os
import spotipy
import tidalapi
import logging
from spotipy.oauth2 import SpotifyOAuth

def main():
    scope = "user-library-read"
    spotify_session = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    tidal_session = tidalapi.Session()
    # # Will run until you visit the printed url and link your account
    # session.login_oauth_simple()
    # logging.info(session.check_login())
    token_type = 'Bearer'
    access_token = os.getenv('TIDAL_ACCESS_TOKEN')
    refresh_token = os.getenv('TIDAL_REFRESH_TOKEN')
    expiry_time = os.getenv('TIDAL_EXPIRY_TIME')
    tidal_session.load_oauth_session(token_type, access_token, refresh_token, expiry_time)


    tidal_playlists = tidal_session.user.playlists()
    tidal_tempo_playlists = []
    for playlist in tidal_playlists:
        tidal_tempo_playlists.append({
            'name': playlist.name,
            'tempo': int(playlist.name),
            'id': playlist.id
        })

    spotify_liked_tracks = spotify_session.current_user_saved_tracks(limit=50, offset=150)

    for item in spotify_liked_tracks['items']:

        spotify_track = item['track']    
        logging.info(f"{spotify_track['artists'][0]['name']} – {spotify_track['name']}")

        spotify_audio_features = spotify_session.audio_features([spotify_track['uri']])[0]
        
        if isinstance(spotify_audio_features, type(None)):
            logging.warning("BPM Not Found")
            continue

        bpm_rounded = 5 * round(spotify_audio_features['tempo'] / 5)
        if bpm_rounded <= 105 or bpm_rounded >= 160:
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
        tidal_target_playlist = tidal_session.playlist([playlist for playlist in tidal_tempo_playlists if playlist['tempo'] == bpm_rounded][0]['id'])
        tidal_target_playlist.add([tidal_search_result['top_hit'].id])

if __name__ == "__main__":
    logging.basicConfig(
        level = os.environ.get('LOGLEVEL', 'INFO').upper(),
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.StreamHandler()
        ]
    )
    logging.info("Start Main")
    main()
    logging.info("Fin")