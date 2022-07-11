#!/usr/bin/env python3

# modules/junodownload.py
# JunoDownload Scraper

from bs4 import Tag
from qtpy import QtCore

from common import getWebPage, openURL, printline, verifyDate
from plugin import Plugin
from scraping import Song, SongScraper

genremap = {
    '50s/60s/rock\'n\'roll/rhythm&blues': '50s-60s-rocknroll-rhythmandblues',
    'ambient/drone': 'ambient-drone',
    'balearic/downtempo': 'downtempo',
    'bass': 'bass',
    'breakbeat': 'breakbeat',
    'broken beat/nu jazz/nu soul': 'broken-beat',
    'coldwave/synth': 'coldwave-synth',
    'dancehall/ragga/reggaeton': 'dancehall-reggae',
    'deep dubstep': 'deep-dubstep',
    'deep house': 'deep-house',
    'dirty dubstep/heavy dubstep/trap/grime': 'dirty-heavy-dubstep',
    'disco/nu disco/re-edits': 'disco',
    'dj tools/acappellas/scratch records': 'dj-tools',
    'drum & bass/jungle': 'drumandbass',
    'dub reggae': 'dub-reggae',
    'electro': 'electro',
    'electro house/electroclash': 'electro-house',
    'euro dance/pop dance': 'dance-pop',
    'experimental/electronic': 'experimental-electronic',
    'footwork/juke': 'footwork-juke',
    'funk/rare groove': 'funk-reissues',
    'funky/club house': 'funky-club-house',
    'gabba': 'gabba',
    'hard house': 'hard-house',
    'hard techno': 'hard-techno',
    'hard trance': 'hard-trance',
    'hardstyle/jumpstyle': 'hardstyle',
    'hip hop/r&b': 'hip-hop',
    'indie/alternative rock': 'indie',
    'industrial/noise': 'industrial-noise',
    'international': 'international',
    'jazz': 'jazz',
    'minimal house/tech house': 'minimal-tech-house',
    'pop': 'pop',
    'pop trance': 'pop-trance',
    'progressive house': 'progressive-house',
    'psychedelic trance/goa trance': 'psy-goa-trance',
    'reggae classics/oldies/ska': 'reggae-classics',
    'rock': 'rock',
    'roots reggae/lovers rock/one drop': 'roots-reggae',
    'scouse house/bouncy house': 'scouse-house',
    'soul': 'soul',
    'soundtracks': 'soundtrack',
    'techno': 'techno-music',
    'uk garage': '4x4-garage',
    'uk hardcore/nu rave': 'uk-hardcore',
    'uplifting trance/progressive trance': 'uplifting-trance'
}

gimmeplugin = {'name': 'JunoDownload',
                 'genres': list(genremap.keys()),
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'Dance MP3 download store with over 2 million tracks available and thousands more added each week.'}

datemap = {
    'Jan': '1',
    'Feb': '2',
    'Mar': '3',
    'Apr': '4',
    'May': '5',
    'Jun': '6',
    'Jul': '7',
    'Aug': '8',
    'Sep': '9',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

baseURL='https://www.junodownload.com/%s/back-cat/releases/%d/?order=date_down'


def scrapeGenre(scraper: SongScraper, genre: str, page: int = 1) -> None:

    # Unfortunately, while the API is still functional, it hasn't been possible to register an API key for years
    # Therefore, fall back to good old HTML scraping
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (genre, page)))
    if not wp:
        return

    # Use a CSS selector to get the table, then select all child divs with class "row gutters-sm jd-listing-item"
    table = wp.select_one('.order-lg-2.order-1.col-lg-9.col-12')
    table = table.find_all('div', class_='row gutters-sm jd-listing-item', recursive=False)

    # Parse the table
    for entry in table:
        printline(scraper, 'Parsing entry...')

        # Date check
        # First, we need to do some magic with date formatting
        # This is because Qt insists on using the user's locale for formatting instead of English
        # And also because 22 is converted to 1922, not 2022
        date = entry.contents[2].div.contents[2].split()
        date[1] = datemap[date[1]]
        date[2] = '20' + date[2]
        date = QtCore.QDate.fromString(' '.join(date), 'dd M yyyy')
        if not verifyDate(date):
            printline(scraper, 'Reached max delta date. Moving on...')
            return

        # Artist + hotfix for Various Artists
        artist = entry.find('div', class_='col juno-artist').contents[0]
        if type(artist) == Tag:
            artist = artist.contents[0]

        # Rest of the data
        album = entry.find('a', class_='juno-title').contents[0]
        songs = entry.find('div', class_='jd-listing-tracklist').contents
        for song in songs:

            # Can't even get the name easily due to shitty formatting
            name = song.contents[1].contents[0].replace('\xa0', ' ').replace('"', '').split(' - ')
            i = len(name)
            audiourl = song.div.button['data-href']
            if i < 3:
                scraper.songfound.emit(Song(name[0], artist, album, genre.title(), audiourl), 'JunoDownload')
            else:
                scraper.songfound.emit(Song(name[1], name[0], album, genre.title(), audiourl), 'JunoDownload')

    # Call this again for the next page
    scrapeGenre(scraper, genre, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Parse each genre if enabled
    for genre, enabled in moduledata.genres.items():
        if enabled:
            printline(scraper, 'Parsing genre', genre + '...')

            # Get genre from the map
            genre = genremap[genre]

            # Run subroutine
            scrapeGenre(scraper, genre)
            break


if __name__ == '__main__':
    print("Run main.py to access the program!")
