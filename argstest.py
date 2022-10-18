import argparse

parser = argparse.ArgumentParser(description='Move Spotify songs to Tidal Playlists')
group = parser.add_mutually_exclusive_group()

group.add_argument('-u', '--url', help='Playlist URL to be moved')
group.add_argument('-ls', '--liked-songs', action='store_true' ,help='Liked songs to be moved')

args = parser.parse_args()
print(args)
parser.print_help()