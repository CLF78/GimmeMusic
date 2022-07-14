#!/usr/bin/env python3

# modules/beatport.py
# Beatport Scraper

from bs4 import NavigableString
from qtpy import QtCore

from common import getLastUse, getWebPage, printline, openURL
from plugin import Plugin
from scraping import Song, SongScraper

genremap = {
    'acapellas': 'acapella',
    'acid': 'acid house',
    'afro-latin': 'afro/latin',
    'afro-house': 'afro house',
    'amapiano': 'amapiano',
    'ambient': 'ambient',
    'bassclub': 'bass/club',
    'bass': 'bass dubstep',
    'bass-house': 'bass house',
    'bassline': 'bassline',
    'big-room': 'big room',
    'bounce': 'bounce',
    'breaks-breakbeat-uk-bass': 'breaks/breakbeat/uk bass',
    'broken': 'broken techno',
    'bass-club': 'club',
    'dance-electro-pop': 'dance/electro pop',
    'dark-disco': 'dark disco',
    'deep': 'deep dnb',
    '140-deep-dubstep-grime': 'deep dubstep',
    'depp-house': 'deep house',
    'deep-tech': 'deep tech',
    'deep-hypnotic': 'deep techno',
    'deep-trance': 'deep trance',
    'downtempo': 'downtempo',
    'driving': 'driving techno',
    'drum-bass': 'drum & bass',
    'dub': 'dub techno',
    'dubstep': 'dubstep',
    'electro-classic-detroit-modern': 'electro',
    'electro-house': 'electro house',
    'ebm': 'electronic body music',
    'electronica': 'electronica',
    'frenchcore': 'frenchcore',
    'full-on': 'full-on psytrance',
    'funk-soul': 'funk/soul',
    'funky-house': 'funky-house',
    'future-bass': 'future bass',
    'future-house': 'future house',
    'future-rave': 'future rave',
    'glitch-hop': 'glitch-hop',
    'global-club': 'global club',
    'gqom': 'gqom',
    'grime': 'grime',
    'halftime': 'halftime dnb',
    'hard-dance-hardcore': 'hard dance/hardcore',
    'hard-house': 'hard house',
    'hard-techno': 'hard techno',
    'hard-trance': 'hard trance',
    'hardstyle': 'hardstyle',
    'house': 'house',
    'indie-dance': 'indie dance',
    'italo': 'italo disco',
    'jackin-house': 'jackin house',
    'jersey-club': 'jersey club',
    'juke-footwork': 'juke/footwork',
    'jump-up': 'jump up',
    'jungle': 'jungle',
    'liquid': 'liquid dnb',
    'mainstage': 'mainstage',
    'melodic-dubstep': 'melodic dubstep',
    'melodic-house-techno': 'melodic house/techno',
    'midtempo': 'midtempo',
    'minimal-deep-tech': 'minimal',
    'nu-disco-disco': 'nu disco',
    'organic-house': 'organic house',
    'peak-time': 'peak time techno',
    'pop': 'pop',
    'progressive-house': 'progressive house',
    'progressive': 'progressive trance/psytrance',
    'psy-trance': 'psytrance',
    'raw': 'raw techno',
    'reggae': 'reggae',
    'reggae-dancehall': 'reggae/dancehall',
    'soulful': 'soulful house',
    'speed-house': 'speed house',
    'tech': 'tech',
    'tech-house': 'tech house',
    'terror': 'terror',
    'trance': 'trance',
    'trap-wave': 'trap/wave',
    'tropical-house': 'tropical house',
    'uk-happy-hardcore': 'uk/happy hardcore',
    'uk-funky': 'uk funky',
    'uk-garage': 'uk garage',
    'uplifting': 'uplifting trance',
    'uptempo': 'uptempo hardcore',
    'vocal': 'vocal trance',
}

gimmeplugin = {'name': 'Beatport',
                 'genres': list(genremap.values()),
                 'author': 'CLF78',
                 'version': '0.1',
                 'description': 'The world\'s largest store for DJs.'}

baseURL='https://www.beatport.com/releases/all?page=%d&sort=release-desc&preorders=false&start-date=%s&end-date=%s'
downloadURL = 'https://www.beatport.com/api/releases/%s/tracks'


def scrapeReleases(scraper: SongScraper, userGenres: dict, startDate: str, endDate: str, page: int = 1) -> None:

    # Get the releases page
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (page, startDate, endDate), clearcookies=True))
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
            foundgenre = False
            genres = [genre['slug'] for genre in track['sub_genres']]
            if not genres:
                genres = [genre['slug'] for genre in track['genres']]
            for genre in genres:
                if genremap.get(genre, '') and userGenres[genremap[genre]]:
                    foundgenre = True
                    break

            # If the genre doesn't match any of the user's enabled genres, skip this entry
            if not foundgenre:
                printline(scraper, 'Genre not matching values:', genres, '. Skipping...')
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
            scraper.songfound.emit(Song(name, ', '.join(artists), album, genremap[genre], audiourl), 'Beatport')

    # Check if it's the last page, and if so return
    pagenum = wp.select_one('.pagination-top-container.pagination-container > .pag-num-list-container')
    if not pagenum.find('a', class_='pag-next', recursive=False):
        return

    # Else call this recursively
    scrapeReleases(scraper, userGenres, startDate, endDate, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Get the date intervals
    endDate = QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    startDate = getLastUse().toString('yyyy-MM-dd')

    # Begin the scrape
    scrapeReleases(scraper, moduledata.genres, startDate, endDate)
    return


if __name__ == '__main__':
    print("Run main.py to access the program!")
