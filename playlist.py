#!/usr/bin/env python3

# playlist.py
# This file defines GimmeMusic's playlist widget.

from qtpy import QtWidgets
from qtpy.QtCore import Qt

from scraping import Song

class Playlist(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Label
        self.label = QtWidgets.QLabel('Playlist', self)

        # Tree
        self.tree = QtWidgets.QTreeWidget(self)

        # Set column count and header texts
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(['✓', 'Name', 'Artist', 'Album', 'Genre', 'Source'])

        # Remove indentation
        self.tree.setIndentation(0)

        # Make selection span all columns and enable uniform row heights
        self.tree.setAllColumnsShowFocus(True)
        self.tree.setUniformRowHeights(True)

        # Prevent moving the first section
        header = self.tree.header()
        header.setFirstSectionMovable(False)

        # Make all sections the same size, except the first one
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(0, int(header.fontMetrics().size(0, '✓').height() * 1.5))

        # Play button
        self.playButton = QtWidgets.QPushButton('Play', self)
        self.playButton.setEnabled(False)

        # Export button
        self.exportSelected = QtWidgets.QPushButton('Export', self)
        self.exportSelected.setEnabled(False)

        # Remove button
        self.removeSelected = QtWidgets.QPushButton('Remove', self)
        self.removeSelected.setEnabled(False)

        # Clear button
        self.clearButton = QtWidgets.QPushButton('Clear', self)
        self.clearButton.setEnabled(False)

        # Add elements to layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.label, 0, 0, 1, 2)
        L.addWidget(self.tree, 1, 0, 1, 2)
        L.addWidget(self.playButton, 2, 0)
        L.addWidget(self.exportSelected, 2, 1)
        L.addWidget(self.removeSelected, 3, 0)
        L.addWidget(self.clearButton, 3, 1)

    def addEntry(self, song: Song, modname: str):
        """
        Adds an entry to the playlist.
        """
        newitem = QtWidgets.QTreeWidgetItem(self.tree, ['', song.name, song.artist, song.album, song.genre, modname])
        newitem.setCheckState(0, Qt.Checked)
        newitem.setData(0, Qt.UserRole, song)

if __name__ == '__main__':
    print("Run main.py to access the program!")
