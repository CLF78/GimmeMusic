#!/usr/bin/env python3

# console.py
# This file defines GimmeMusic's console widget.

from qtpy import QtWidgets


class Console(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Top label
        self.label = QtWidgets.QLabel('Console', self)

        # Output
        self.textinput = QtWidgets.QTextEdit('Welcome to GimmeMusic!', self)
        self.textinput.setReadOnly(True)
        self.textinput.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        # Clear button
        self.clearbutton = QtWidgets.QPushButton('Clear Console', self)
        self.clearbutton.clicked.connect(lambda: self.textinput.setText('Welcome to GimmeMusic!'))

        # Make a layout and set it
        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addWidget(self.label)
        lyt.addWidget(self.textinput)
        lyt.addWidget(self.clearbutton)

if __name__ == '__main__':
    print("Run main.py to access the program!")
