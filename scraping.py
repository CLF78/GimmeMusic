import importlib
import sys

from PyQt5 import QtCore

import globalz

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
    finished = QtCore.pyqtSignal()
    textappended = QtCore.pyqtSignal(str)
    songfound = QtCore.pyqtSignal(Song)

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
        self.printline('Initiating song scrape...')

        # Run each module
        for modname, module in self.modulelist.items():

            # Run only if module is enabled
            if module.enabled:
                self.printline('Running module', modname + '...')

                # Run the module's main function and process the output
                try:
                    func = getattr(module.module, globalz.mainfunc, None)
                    songs = func(module)
                    for song in songs:
                    	self.songfound.emit(song)
                except Exception as e:
                    self.printline('Failed to execute module', modname + ':', e)

        # Emit event when loop ends
        self.finished.emit()

    def printline(self, *args):
        """
        Prints text to the console. Works almost like the print function.
        """
        # Join the arguments together and emit event
        self.textappended.emit(' '.join(map(str, args)))

    def addToList(song):
        """
        Adds a given song to the playlist.
        """
        self.songadded.emit(song)
