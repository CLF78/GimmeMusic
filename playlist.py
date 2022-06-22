#!/usr/bin/env python3

# playlist.py
# This file defines GimmeMusic's playlist widget.

from qtpy import QtWidgets


class Playlist(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = QtWidgets.QLabel('Playlist', self)

        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setHeaderHidden(True)

        self.exportSelected = QtWidgets.QPushButton('Export Selected', self)
        self.exportSelected.setEnabled(False)

        self.removeSelected = QtWidgets.QPushButton('Remove Selected', self)
        self.removeSelected.setEnabled(False)

        # Add elements to layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.label, 0, 0, 1, 2)        
        L.addWidget(self.tree, 1, 0, 1, 2)
        L.addWidget(self.exportSelected, 2, 0)
        L.addWidget(self.removeSelected, 2, 1)

if __name__ == '__main__':
    print("Run main.py to access the program!")
