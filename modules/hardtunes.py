#!/usr/bin/env python3

# modules/hardtunes.py
# HardTunes Scraper

import re

from bs4.element import Tag, NavigableString
from qtpy import QtCore

from common import getWebPage, openURL, printline, verifyDate
from plugin import Plugin
from scraping import Song, SongScraper

gimmeplugin = {'name': 'HardTunes',
                 'genres': ['hardcore', 'terror', 'frenchcore', 'hardstyle', 'early rave', 'crossbreed'],
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'The world\'s best hardcore download portal. Get the latest tracks and albums in MP3 or WAV format.'}

baseURL = 'https://www.hardtunes.com/%s/page/%d'
downloadURL = 'https://www.hardtunes.com/call/add/playlist'
playlistURL = 'https://www.hardtunes.com/call/view/playlist'


def scrapeSong(scraper: SongScraper, genre: str, id: str, album: str = '') -> None:

    # Use a POST request to get the rest of the metadata
    printline(scraper, 'Scraping song...')
    resp = openURL(scraper, 'post', downloadURL, clearcookies=True, data={'product_id': id})
    if not resp:
        return

    # Build class and emit event
    resp = resp.json()['player']
    a = resp['title'].split('<br/>')
    scraper.songfound.emit(Song(a[0], a[1], album, genre.title(), resp['mp3']), 'HardTunes')


def scrapeAlbum(scraper: SongScraper, genre: str, album: str, id: str):

    # Use a POST+GET request to get the metadata (will it work?)
    printline(scraper, 'Scraping album...')
    resp = openURL(scraper, 'post', downloadURL, clearcookies=True, data={'album_id': id})
    if not resp:
        return
    resp = getWebPage(scraper, openURL(scraper, 'get', playlistURL))
    if not resp:
        return

    for entry in resp.body.div.children:

        # This website returns broken HTML which yields children consisting of a single newline. Ignore them
        if type(entry) == NavigableString:
            continue

        # Parse the id and call scrapeSong (with more broken HTML bullshit)
        entry = entry.find('div', class_='release-list-item-info-primary')
        id = entry.p.a['href'].split('/')[-1]
        scrapeSong(scraper, genre, id, album)


def scrapeGenre(scraper: SongScraper, genre: str, page: int = 1) -> None:

    # Get page, exit if not found
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (genre, page), silent=False))
    if not wp:
        return

    # Get the entry table:
    # Use a CSS selector to find the release list div -> select all children
    for entry in wp.body.select_one('.panel-body > .release-list-normal.release-list.row').children:

        # Get initial info
        printline(scraper, 'Parsing entry...')
        url = entry.div.a['href']
        info2 = entry.contents[1].contents[1]
        type = info2.p.a.string
        datestr = info2.contents[1].string

        # If type is mix, ignore this entry, else check if it's an album
        if type == 'Mix':
            printline(scraper, 'Skipping mix entry...')
            continue
        isAlbum = type != 'Single tune'

        # If date is today, assume it is allowed
        if datestr == 'Today':
            pass

        # If date is yesterday, do a rudimentary check
        elif datestr == 'Yesterday':
            date = QtCore.QDate.currentDate().addDays(-2)
            if not verifyDate(date):
                printline(scraper, 'Reached max delta date. Moving on...')
                return

        # For other dates of the week, we unfortunately have to open the page
        # Checking the Last-Modified attribute won't work because the files are uploaded several days before the official release
        # So, get the web page. If it fails, keep going
        elif datestr == 'This week':
            subpage = openURL(scraper, 'get', url)
            if not subpage:
                continue

            date = QtCore.QDate.fromString(re.search(r'\d{4}-\d{2}-\d{2}', subpage.text).group(), 'yyyy-MM-dd')
            if not verifyDate(date):
                printline(scraper, 'Reached max delta date. Moving on...')
                return

        # Other values are automatically out of range
        else:
            printline(scraper, 'Reached max delta date. Moving on...')
            return

        # Act accordingly
        if isAlbum:
            scrapeAlbum(scraper, genre, entry.contents[1].div.p.a.string, url.split('/')[-1])
        else:
            scrapeSong(scraper, genre, url.split('/')[-1])

    # Call this again for the next page
    scrapeGenre(scraper, genre, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Parse each genre if enabled
    for genre, enabled in moduledata.genres.items():
        if enabled:
            printline(scraper, 'Parsing genre', genre.title() + '...')

            # Small fixes for genre names
            genre = genre.replace(' ', '-')

            # Run subroutine
            scrapeGenre(scraper, genre)


if __name__ == '__main__':
    print("Run main.py to access the program!")
