#!/usr/bin/env python3

# modules/test.py
# This is a test plugin for GimmeMusic, intended to showcase its basic structure.

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
# - The SongScraper instance, required for printing to the console from a plugin
# - A dictionary containing the module's settings indicated by the user
# The return value is a list of Song instances, which will be added to the playlist widget after this function has run
def scrapeMain(scraper: SongScraper, moduledata: dict) -> list:
    return [Song('Test Song 1', audiourl='https://doc.qt.io/qt-5/qtreewidget.html')]

if __name__ == '__main__':
    print("Run main.py to access the program!")
