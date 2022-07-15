#!/usr/bin/env python3

# modules/beatport.py
# Beatport Scraper

import json
import os

from bs4 import NavigableString
from qtpy import QtCore

from common import getAbsPath, getLastUse, getWebPage, printline, openURL
from plugin import Plugin
from scraping import Song, SongScraper

genredata = None

# Open and parse the genre data
def createGenreData() -> list:
    global genredata

    # Check if the file exists
    genrefile = getAbsPath('beatportgenres.json')
    if not os.path.isfile(genrefile):
        raise Exception('Genre file not found!')

    # Read it (do not catch exceptions, let the plugin scanner do that)
    with open(genrefile) as f:
        data = f.read()
    genredata = json.loads(data)

    # Parse it
    results = []
    for genre in genredata['results']:
        results.append(genre['name'].lower())
        for subgenre in genre['sub_genres']:
            subgenre = subgenre['name'].lower()
            if subgenre not in results:
                results.append(subgenre)

    # Sort it and return it
    results.sort()
    return results


gimmeplugin = {'name': 'Beatport',
                 'genres': createGenreData(),
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'The world\'s largest store for DJs.'}

baseURL='https://www.beatport.com/genre/%s/%d/releases?page=%d&sort=release-desc&preorders=false&start-date=%s&end-date=%s'
downloadURL = 'https://www.beatport.com/api/releases/%s/tracks'


def getTrackGenre(modulegenres: dict, track: dict) -> str:
    """
    Checks if the subgenre is enabled (or the genre if no subgenres are present).
    """
    genrelist = track['sub_genres'] if track['sub_genres'] else track['genres']
    for genre in genrelist:
        genre = genre['name']
        if modulegenres[genre.lower()]:
            return genre
    return ''


def scrapeGenre(scraper: SongScraper, modulegenres: dict, genreJson: dict, startDate: str, endDate: str, page: int = 1) -> None:

    # Get the releases page
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (genreJson['slug'], genreJson['id'], page, startDate, endDate), silent=False, clearcookies=True))
    if not wp:
        return

    # Get the release table using a CSS selector, then iterate through it
    table = wp.body.select_one('.filter-page-releases-list.ec-bucket.bucket-items').contents
    for entry in table:

        # Skip strings
        if type(entry) == NavigableString:
            continue

        # Get API response
        printline(scraper, 'Parsing entry...')
        id = entry['data-ec-id']
        resp = openURL(scraper, 'get', downloadURL % id)
        if not resp:
            return

        # Get all the metadata
        resp = resp.json()
        for track in resp['tracks']:

            # Subgenre/genre checks
            # If the track has subgenres and none of them is enabled, skip entry
            genre = getTrackGenre(modulegenres, track)
            if not genre:
                printline(scraper, 'Genre/subgenre not enabled. Skipping...')
                continue

            # Check if available for preview
            audiourl = track['preview']['mp3']['url']
            if not audiourl:
                audiourl = track['preview']['mp4']['url']
            if not audiourl:
                continue

            # Get the remaining metadata
            name = track['name']
            mix = track['mix']
            if mix:
                name += f' ({mix})'

            artists = [artist['name'] for artist in track['artists']]
            artists += [remixer['name'] for remixer in track['remixers']]

            album = track['release']['name']

            # Emit event
            scraper.songfound.emit(Song(name, ', '.join(artists), album, genre, audiourl), 'Beatport')

    # Check if it's the last page, and if so return
    pagenum = wp.select_one('.pagination-top-container.pagination-container > .pag-num-list-container')
    if not pagenum.find('a', class_='pag-next'):
        return

    # Else call this recursively
    scrapeGenre(scraper, modulegenres, genreJson, startDate, endDate, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Get the date intervals
    endDate = QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    startDate = getLastUse().toString('yyyy-MM-dd')

    # Parse the genre JSON
    for entry in genredata['results']:

        # If the main genre matches, scrape it
        if moduledata.genres[entry['name'].lower()]:
            printline(scraper, 'Parsing genre', entry['name'] + '...')
            scrapeGenre(scraper, moduledata.genres, entry, startDate, endDate)

        # If at least one subgenre matches, also scrape it
        else:
            for subentry in entry['sub_genres']:
                if moduledata.genres[subentry['name'].lower()]:
                    printline(scraper, 'Parsing genre', subentry['name'] + '...')
                    scrapeGenre(scraper, moduledata.genres, entry, startDate, endDate)
                    break


if __name__ == '__main__':
    print("Run main.py to access the program!")
