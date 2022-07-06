#!/usr/bin/env python3

# scraping.py
# This file defines GimmeMusic's scraping functionality.

import requests
from qtpy import QtCore
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

import globalz
from common import printline


class Song:
    """
    Song metadata holder class.
    """
    def __init__(self, name='Untitled', artist='Unknown', album='', genre='', audiourl=''):
        self.name = name
        self.artist = artist
        self.album = album
        self.genre = genre
        self.audiourl = audiourl

class SongScraper(QtCore.QObject):
    """
    Plugin runner (this runs on a separate thread from the GUI).
    """
    finished = QtCore.Signal()
    textappended = QtCore.Signal(str)
    songfound = QtCore.Signal(Song, str)

    def __init__(self, parent):
        """
        Modified init function so we have access to the modulelist without accessing the rest of the program
        """
        super().__init__()
        self.modulelist = parent.modulelist
        self.terminate = False
        parent.stopscrape.connect(lambda: setattr(self, 'terminate', True))

    def run(self):
        printline(self, 'Initiating song scrape...')

        # Create the requests session
        self.session = CacheControl(requests.Session(), cache=FileCache(globalz.cachedir))

        # Run each module
        for modname, module in self.modulelist.items():

            # If the thread was terminated, quit the loop immediately
            if self.terminate:
                break

            # Run module only if enabled
            if module.enabled:
                printline(self, 'Running module', modname + '...')

                # Run the module's main function and process the output
                try:
                    func = getattr(module.module, globalz.mainfunc, None)
                    func(self, module)
                except Exception as e:
                    printline(self, 'Failed to execute module', modname + ':', e)

        # Emit event when loop ends
        self.finished.emit()

if __name__ == '__main__':
    print("Run main.py to access the program!")
