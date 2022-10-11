#!/usr/bin/env python3

# modules/undergroundtekno.py
# UndergroundTekno Scraper

from bs4.element import Tag
from qtpy import QtCore

from common import getWebPage, openURL, printline, verifyDate
from plugin import Plugin
from scraping import Song, SongScraper

gimmeplugin = {'name': 'UndergroundTekno',
                 'genres': ['hardtek-tribe', 'frenchcore-hardcore', 'raggatek-jungletek', 'psytek-psytrance'],
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'French physical/digital music shop.'}

baseURL = 'https://download.undergroundtekno.com/en/categories/%s/%s/%d'
downloadURL = 'https://download.undergroundtekno.com/sounds/play/album/%s'
locale = QtCore.QLocale(QtCore.QLocale.C) # for date parsing


def scrapeSong(scraper: SongScraper, page: Tag) -> None:
    page = page.find('div', class_='product-inner')

    # Fill entry up
    newentry = Song(page.h2.a.string, album=page.h2.a.string, genre=page.div.span.string)
    newentry.artist = ', '.join([artist.string for artist in page.find('div', class_='product-artists').find_all('a')])
    newentry.audiourl = downloadURL % page.h2.a['href'].split('/')[-1]
    scraper.songfound.emit(newentry, 'UndergroundTekno')


def scrapeAlbum(scraper: SongScraper, page: Tag, album: str, genre: str) -> None:

    # Get the page table and fill each entry
    for row in page.select_one('.table-product-tracks').tbody.find_all('tr'):
        name = row.find('td', class_='title').string
        artists = ', '.join([entry.string for entry in row.find_all('a', class_='product-artists')])
        audiourl = row.select_one('.inline-playable')['href']
        scraper.songfound.emit(Song(name, artists, album, genre, audiourl), 'UndergroundTekno')


def scrapeGenre(scraper: SongScraper, genre: str, category: str, page: int = 1) -> None:

    # Get page, exit if not found
    wp = getWebPage(scraper, openURL(scraper, 'get', baseURL % (genre, category, page), silent=False, clearcookies=True))
    if not wp:
        return

    # Get the entry table:
    # Use a CSS selector to find the category div -> select each relevant entry
    table = wp.body.select_one(f'#tab-tracks').select('div.col-lg-2.col-md-3.col-sm-6.col-xs-12')
    for entry in table:

        # Get inner div
        entry = entry.div

        # Filter out pre-orders
        btntext = entry.find('div', class_='product-inner').find('div', class_='product-actions').a.contents
        if len(btntext) > 1 and btntext[1] == ' Pre-order':
            printline(scraper, 'Skipping pre-order entry...')
            continue

        # Get the webpage to check the date
        prodpg = getWebPage(scraper, openURL(scraper, 'get', entry.div.a['href']))
        if not prodpg:
            return

        # Get the date
        datestr = prodpg.body.select_one('h5').string.replace('Sortie le ', '').lower()
        date = locale.toDate(datestr, 'dd dddd MMMM yyyy')
        if not verifyDate(date):
            printline(scraper, 'Reached max delta date. Moving on...')
            return

        # Act depending on the scraped content
        if category == 'albums':
            entry = entry.find('div', class_='product-inner')
            scrapeAlbum(scraper, prodpg, entry.h2.a.string, entry.div.span.string)
        else:
            scrapeSong(scraper, entry)

    # Recursively scrape the next page
    scrapeGenre(scraper, genre, category, page + 1)


def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Parse each genre if enabled
    for genre, enabled in moduledata.genres.items():
        if enabled:
            printline(scraper, 'Parsing genre', genre + '...')

            # Run subroutine
            for category in ['tracks', 'albums']:
                scrapeGenre(scraper, genre, category)


if __name__ == '__main__':
    print("Run main.py to access the program!")
