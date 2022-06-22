import importlib
import sys

from qtpy import QtCore

import globalz
from common import printline

class Song:
    """
    Generic class that stores all the info required by the program.
    """
    def __init__(self, name='Unknown Name', artist='Unknown Artist', album='Unknown Album', genre='Unknown Genre', coverurl='', audiourl=''):
        self.name = name
        self.artist = artist
        self.album = album
        self.genre = genre
        self.coverurl = coverurl
        self.audiourl = audiourl

class SongScraper(QtCore.QObject):
    finished = QtCore.Signal()
    textappended = QtCore.Signal(str)
    songfound = QtCore.Signal(Song)

    def __init__(self, modulelist):
        """
        Modified init function so we have access to the modulelist without accessing the rest of the program
        """
        super().__init__()
        self.modulelist = modulelist

    def run(self):
        """
        The main function
        """
        printline(self, 'Initiating song scrape...')

        # Run each module
        for modname, module in self.modulelist.items():

            # Run only if module is enabled
            if module.enabled:
                printline(self, 'Running module', modname + '...')

                # Run the module's main function and process the output
                try:
                    func = getattr(module.module, globalz.mainfunc, None)
                    songs = func(module)
                    for song in songs:
                    	self.songfound.emit(song)
                except Exception as e:
                    printline(self, 'Failed to execute module', modname + ':', e)

        # Emit event when loop ends
        self.finished.emit()

    def addToList(song):
        """
        Adds a given song to the playlist.
        """
        self.songadded.emit(song)
