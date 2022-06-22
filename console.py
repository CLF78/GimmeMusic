from qtpy import QtWidgets


class Console(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Top label
        self.label = QtWidgets.QLabel('Console', self)

        # Output
        self.textinput = QtWidgets.QTextEdit('Welcome to AngerList!', self)
        self.textinput.setReadOnly(True)

        # Clear button
        self.clearbutton = QtWidgets.QPushButton('Clear Console', self)
        self.clearbutton.clicked.connect(lambda: self.textinput.setText('Welcome to AngerList!'))

        # Make a layout and set it
        lyt = QtWidgets.QGridLayout(self)
        lyt.addWidget(self.label, 0, 0)
        lyt.addWidget(self.textinput, 1, 0)
        lyt.addWidget(self.clearbutton, 2, 0)
