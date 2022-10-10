#!/usr/bin/env python3

# modules/test.py
# This is a test plugin for GimmeMusic, intended to showcase its basic structure.

from plugin import Plugin, PluginScanner
from scraping import Song, SongScraper

# Metadata (variable must be named "gimmeplugin" for the plugin to be detected)
# All fields except "genres" are case-insensitive (genres MUST be lowercase)
# name = plugin name (string, required)
# genres = supported genres, each separately toggleable from settings (list, optional)
# author = plugin author (string, optional)
# version = plugin version (string, optional)
# description = a brief description (string, optional)
gimmeplugin = {'name': 'Test Plugin',
                 'genres': ['house', 'techno'],
                 'author': 'CLF78',
                 'version': 'TEST',
                 'description': 'Test plugin.'}

# Main scraping function
# This will be called by the scraper thread if the plugin is enabled
# The arguments are:
# - The SongScraper instance, required for printing to the console and emitting songfound events
# - The module instance, containing the settings indicated by the user
# No return value is expected
def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # To add songs to the playlist, emit a songfound event with a Song class instance and the source name
    # Source name can be grabbed from the module or sent as a string directly
    scraper.songfound.emit(Song('Test Song 1', audiourl='https://doc.qt.io/qt-5/qtreewidget.html'), moduledata.name)


# Main scan function (optional)
# This is run when the plugin is detected and imported
# The arguments are:
# - The PluginScanner instance, required for printing to the console
# - The module instance, containing the settings indicated by the user
# Return True if the plugin should be added, else return False
def scanMain(scanner: PluginScanner, moduledata: Plugin) -> bool:
    return False


if __name__ == '__main__':
    print("Run main.py to access the program!")
