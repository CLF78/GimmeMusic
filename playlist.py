#!/usr/bin/env python3

# playlist.py
# This file defines GimmeMusic's playlist widget.

import webbrowser

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Qt

from common import printline
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
        # Allow multiple selection
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.tree.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)

        # Set up events
        self.tree.itemDoubleClicked.connect(self.handleOpen)
        self.tree.itemSelectionChanged.connect(self.handleSelection)
        self.tree.itemChanged.connect(self.handleRename)
        self.tree.itemClicked.connect(self.updateButtons)

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
        self.exportSelected.clicked.connect(self.exportEntry)

        # Remove button
        self.removeSelected = QtWidgets.QPushButton('Remove', self)
        self.removeSelected.setEnabled(False)
        self.removeSelected.clicked.connect(self.removeEntry)

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
        newitem.setCheckState(0, Qt.Unchecked)
        newitem.setData(0, Qt.UserRole, song)
        newitem.setFlags((newitem.flags() | Qt.ItemIsEditable) ^ Qt.ItemIsDropEnabled)
        self.updateButtons()

    def removeEntry(self):
        """
        Removes the checked entries from the playlist.
        """
        for i in range(self.tree.topLevelItemCount() - 1, -1, -1):
            if self.tree.topLevelItem(i).checkState(0) == Qt.Checked:
                self.tree.takeTopLevelItem(i)
        self.updateButtons()

    def exportEntry(self):
        """
        Exports the playlist to a M3U file.
        """
        file = QtWidgets.QFileDialog.getSaveFileName(self,
                                                'Save Playlist',
                                                'playlist.m3u',
                                                'Playlists (*.m3u);;')[0]

        printline(self, 'Exporting playlist to', file + '...')
        with open(file, 'w', encoding='utf-8', errors='replace') as f:
            # Write header
            f.write('#EXTM3U\n')

            # Get all checked items
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item.checkState(0) == Qt.Checked:
                    data = item.data(0, Qt.UserRole)

                    # Write the data
                    f.write(f'#EXTINF:-1,{data.artist} - {data.name} ({data.album})\n')
                    f.write(f'{data.audiourl}\n')

        printline(self, 'Export complete!')

    def clearPlaylist(self):
        """
        Clears the playlist.
        """
        self.tree.clear()
        self.updateButtons()

    def updateButtons(self):
        """
        Updates the Export and Remove buttons if any item is selected
        """
        enabled = False
        for i in range(self.tree.topLevelItemCount()):
            if self.tree.topLevelItem(i).checkState(0) == Qt.Checked:
                enabled = True
                break

        self.clearButton.setEnabled(bool(self.tree.topLevelItemCount()))
        self.exportSelected.setEnabled(enabled)
        self.removeSelected.setEnabled(enabled)

    def handleRename(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """
        Updates/reverts song metadata changes.
        """
        # Check if data exists
        data = item.data(0, Qt.UserRole)
        if not data:
            return

        # Get new and old text
        fieldname = ['name', 'artist', 'album', 'genre'][column-1]
        newtext = item.text(column)
        oldtext = getattr(data, fieldname)

        # If unchanged, do nothing
        if newtext != oldtext:

            # If new text is empty, reset it, else update the data
            if newtext:
                setattr(data, fieldname, newtext)
            else:
                item.setText(column, oldtext)

    def handleSelection(self):
        """
        Marks items as checked if they are selected, otherwise unchecks them.
        """
        selected = self.tree.selectedItems()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(0, (item in selected) * 2)

        # Update buttons
        self.updateButtons()

    def handleOpen(self, song: QtWidgets.QTreeWidgetItem, column: int):
        """
        Opens a song in the browser if double clicked.
        """
        if column != 0:
            webbrowser.open(song.data(0, Qt.UserRole).audiourl)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """
        Filters drag events to disable ordering in the playlist.
        """
        if event.type() == QtCore.QEvent.ChildAdded:
            self.tree.header().setSortIndicator(-1, 0)
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    print("Run main.py to access the program!")
