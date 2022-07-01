#!/usr/bin/env python3

# playlist.py
# This file defines GimmeMusic's playlist widget.

import webbrowser

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Qt

from scraping import Song

class EditorDelegate(QtWidgets.QItemDelegate):
    """
    Empty delegate class to prevent editing some columns of the playlist.
    """
    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        return None


class Playlist(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Label
        self.label = QtWidgets.QLabel('Playlist', self)

        # Tree
        self.tree = QtWidgets.QTreeWidget(self)

        # Install an event filter to intercept drag events
        self.tree.installEventFilter(self)

        # Disable editing column 0 and 5 by using an empty delegate
        delegate = EditorDelegate(self)
        self.tree.setItemDelegateForColumn(0, delegate)
        self.tree.setItemDelegateForColumn(5, delegate)

        # Allow editing list items by selecting and clicking
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)

        # Set up events
        self.tree.itemDoubleClicked.connect(lambda song: webbrowser.open(song.data(0, Qt.UserRole).audiourl))

        # Set column count and header texts
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(['✓', 'Name', 'Artist', 'Album', 'Genre', 'Source'])

        # Remove indentation
        self.tree.setIndentation(0)

        # Make selection span all columns and enable uniform row heights
        self.tree.setAllColumnsShowFocus(True)
        self.tree.setUniformRowHeights(True)

        # Enable reordering items
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Prevent moving the first section
        header = self.tree.header()
        header.setFirstSectionMovable(False)

        # Make all sections the same size, except the first one
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(0, int(header.fontMetrics().size(0, '✓').height() * 1.5))

        # Export button
        self.exportSelected = QtWidgets.QPushButton('Export', self)
        self.exportSelected.setEnabled(False)

        # Remove button
        self.removeSelected = QtWidgets.QPushButton('Remove', self)
        self.removeSelected.setEnabled(False)

        # Clear button
        self.clearButton = QtWidgets.QPushButton('Clear', self)
        self.clearButton.setEnabled(False)
        self.clearButton.clicked.connect(self.clearPlaylist)

        # Add elements to layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.label, 0, 0, 1, 2)
        L.addWidget(self.tree, 1, 0, 1, 2)
        L.addWidget(self.exportSelected, 2, 0, 1, 2)
        L.addWidget(self.removeSelected, 3, 0)
        L.addWidget(self.clearButton, 3, 1)

    def addEntry(self, song: Song, modname: str):
        """
        Adds an entry to the playlist.
        """
        newitem = QtWidgets.QTreeWidgetItem(self.tree, ['', song.name, song.artist, song.album, song.genre, modname])
        newitem.setCheckState(0, Qt.Checked)
        newitem.setData(0, Qt.UserRole, song)
        newitem.setFlags((newitem.flags() | Qt.ItemIsEditable) ^ Qt.ItemIsDropEnabled)

    def clearPlaylist(self):
        """
        Clears the playlist
        """
        self.tree.clear()
        self.clearButton.setEnabled(False)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """
        Filters drag events to disable ordering in the playlist.
        """
        if event.type() == QtCore.QEvent.ChildAdded:
            self.tree.header().setSortIndicator(-1, 0)
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    print("Run main.py to access the program!")
