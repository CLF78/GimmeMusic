#!/usr/bin/env python3

# modules/test.py
# This is a test plugin for GimmeMusic, intended to showcase its basic structure.

from plugin import Plugin
from scraping import Song, SongScraper

# Metadata (variable must be named "gimmeplugin" for the plugin to be detected)
# All fields except "genres" are case-insensitive (genres MUST be lowercase)
# name = plugin name (string, required)
# genres = supported genres, each separately toggleable from settings
# author = plugin author (string, optional)
# version = plugin version (string, optional)
# description = a brief description (string, optional)
gimmeplugin = {'name': 'Test Plugin',
                 'genres': ['hardcore', 'frenchcore'],
                 'author': 'CLF78',
                 'version': 'TEST',
                 'description': 'Test plugin.'}

# Main scraping function
# This will be called by the scraper thread if the plugin is enabled
# The arguments are:
# - The SongScraper instance, required for printing to the console and emitting songfound events
# - The module instance, containing the settings indicated by the user
# No return value is expected
def scrapeMain(scraper: SongScraper, moduledata: Plugin):

    # To add songs to the playlist, emit a songfound event with a Song class instance and the source name
    # Source name can be grabbed from the module or sent as a string directly
    scraper.songfound.emit(Song('Test Song 1', audiourl='https://doc.qt.io/qt-5/qtreewidget.html'), moduledata.name)


if __name__ == '__main__':
    print("Run main.py to access the program!")
