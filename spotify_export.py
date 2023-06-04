#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
from typing import List

import spotipy
from dotenv import load_dotenv
from spotipy import SpotifyOAuth


class SpotifyImportException(Exception):
    """Catch all exception for SpotifyImport."""
    pass


def scoped(scopes: List[str]):
    return ' '.join(scopes)


class SpotifyExport:

    def __init__(self, playlist):
        self.playlist = playlist

        load_dotenv()
        scope = scoped(['playlist-read-private', 'user-library-read'])
        # scope = scoped(['playlist-modify-private', 'user-library-modify', 'playlist-read-private'])
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))

    @staticmethod
    def _playlist_link_to_id(playlist_link: str):
        # playlist link likes: https://open.spotify.com/playlist/{id}?si={xxxxx}
        return playlist_link.split('/')[-1].split('?')[0]

    def run(self):
        playlist_id = self._playlist_link_to_id(self.playlist)
        print(f"Exporting playlist {playlist_id}...")
        items_result = self.sp.playlist_items(playlist_id, limit=5, additional_types=['track'])
        items = []
        while items_result['next']:
            items.extend(items_result['items'])
            items_result = self.sp.next(items_result)
        items.extend(items_result['items'])

        with open(f"spotify_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # artist,album,title
            writer.writerow(['artist', 'album', 'title'])
            for item in items:
                track = item['track']
                writer.writerow([track['artists'][0]['name'], track['album']['name'], track['name']])

        print(f"Exported {len(items)} songs to CSV file.")


def main():
    parser = argparse.ArgumentParser(
        description='Simple CLI utility to export Spotify playlist to CSV file.')
    parser.add_argument('playlist', help='the link of playlist to export')

    args = parser.parse_args()

    spotify_export = SpotifyExport(args.playlist)
    spotify_export.run()


if __name__ == '__main__':
    main()
