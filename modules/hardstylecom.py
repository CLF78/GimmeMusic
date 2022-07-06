#!/usr/bin/env python3

# modules/hardstylecom.py
# Hardstyle.com Plugin

from bs4.element import Tag
from qtpy import QtCore

from common import getWebPage, openURL, printline, verifyDate
from plugin import Plugin
from scraping import Song, SongScraper

gimmeplugin = {'name': 'Hardstyle.com',
                 'genres': ['hardstyle', 'hardcore', 'freestyle', 'hard dance', 'frenchcore', 'uptempo', 'happy hardcore'],
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'Leading download portal for the harder styles.'}

baseURL = 'https://music.hardstyle.com/%s-releases/page/%d'
downloadURL = 'https://preview.content.hardstyle.com/index2.php?id=%s'


def scrapeSong(scraper: SongScraper, data: Tag) -> None:

    # First, get the name
    name = data.find('meta', itemprop='name')['content']

    # Then get the album
    # This attribute may be empty or non-existant, and if so re-use the name
    album = data.find('meta', itemprop='inAlbum')
    if not album or not album['content']:
        album = name
    else:
        album = album['content']

    # Append the version to the name if present
    version = data.find('meta', itemprop='version')
    if version:
        name += ' (%s)' % version['content']        

    # Get the rest of the data
    artist = data.find('meta', itemprop='byArtist')['content']
    genre = data.find('meta', itemprop='genre')['content']
    audiourl = downloadURL % data.link['href'].split('/')[-1]

    # Emit event
    scraper.songfound.emit(Song(name, artist, album, genre, audiourl), 'Hardstyle.com')


def scrapeAlbum(scraper: SongScraper, data: Tag) -> None:

    # Simply parse all the divs inside this tag as an individual song
    for entry in data.find_all('div', recursive=False):
        scrapeSong(scraper, entry)


def scrapeGenre(scraper: SongScraper, genre: str, page: int = 1) -> None:

    # Get page, exit if not found
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (genre, page), silent=False, clearcookies=True))
    if not wp:
        return

    # Get the entry table:
    # Use a CSS selector to find tbody -> select all "tr"s with a class attribute set
    table = wp.body.select_one('.p-10.content > .list > tbody').find_all('tr', class_=True, recursive=False)
    for entry in table:
        printline(scraper, 'Parsing entry...')

        # Unfortunately this website is crappy, so part of the data is hidden inside the entry's page
        # Checking the Last-Modified attribute won't work because the audio files are uploaded several days before the official release
        # So, get the web page. If it fails, keep going
        wp = getWebPage(scraper, openURL(scraper, 'get', entry.td.a['href']))
        if not wp:
            continue

        # Get the info using a CSS selector
        data = wp.select_one('#column-middle')

        # Check release date: div id="column-middle" -> div class="box" -> meta itemprop="releaseDate"
        # If delta date is reached, exit immediately
        date = QtCore.QDate.fromString(data.contents[1].contents[1]['content'], 'dd.MM.yyyy')
        ret = verifyDate(date)
        if not ret:
            printline(scraper, 'Reached max delta date. Moving on...')
            return

        # Check if it's an album and act accordingly
        data = data.div
        isAlbum = data['itemtype'].endswith('m')
        if isAlbum:
            scrapeAlbum(scraper, data)
        else:
            scrapeSong(scraper, data)

    # Recursively scrape the next page
    scrapeGenre(scraper, genre, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Parse each genre if enabled
    for genre, enabled in moduledata.genres.items():
        if enabled:
            printline(scraper, 'Parsing genre', genre + '...')

            # Small fixes for genre names
            genre = genre.replace('hap', 'uk hap').replace(' ', '-')

            # Run subroutine
            scrapeGenre(scraper, genre)


if __name__ == '__main__':
    print("Run main.py to access the program!")
