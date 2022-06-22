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
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(self.label)        
        L.addWidget(self.tree)

        # Put the push buttons to a separate grid layout so that we can stretch the widget properly
        btL = QtWidgets.QGridLayout()
        btL.addWidget(self.exportSelected, 0, 0)
        btL.addWidget(self.removeSelected, 0, 1)
        L.addLayout(btL)

if __name__ == '__main__':
    print("Run main.py to access the program!")
