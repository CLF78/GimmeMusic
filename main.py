#!/usr/bin/env python3

# main.py
# This is the main executable for GimmeMusic.

# TODO: lxml import check
# TODO: add __main__ check to every other file

# Python version check
# Currently, QtPy only supports Python 3.7+, so we follow suit
import sys
if sys.version_info < (3, 7):
    raise Exception('Please update your copy of Python to 3.7 or greater. Currently running on: ' + sys.version.split()[0])

# Standard imports
import configparser
import time
import traceback
from io import StringIO

# If any other error occurs, let QtPy throw its own exceptions without intervention
try:
    from qtpy import QtCore, QtGui, QtWidgets
except ImportError:
    raise Exception('QtPy is not installed in this Python environment. Go online and download it.')

try:
    import requests
except ImportError:
    raise Exception('requests is not installed in this Python environment. Go online and download it.')

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise Exception('BeautifulSoup4 is not installed in this Python environment. Go online and download it.')

# Local imports
# Make sure all are imported correctly
try:
    import globalz
    from common import printlineInternal
    from console import Console
    from playlist import Playlist
    from plugin import PluginScanner, Plugin
    from scraping import SongScraper, Song
    from settings import Settings, readconfig, writeconfig
except ImportError:
    raise Exception("One or more program components are missing! Quitting...")


def excepthook(*exc_info):
    """
    Custom unhandled exceptions handler
    """
    # Strings
    separator = '-' * 80
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
    msg1 = 'An unhandled exception occurred. Please report the problem to CLF78.'
    msg2 = 'A log will be written to "log.txt".'
    msg3 = 'Error information:'
    msg4 = ''.join(traceback.format_exception(*exc_info))

    # Write log to file
    try:
        with open(globalz.logfile, "w") as f:
            f.write('\n'.join([separator, timeString, separator, msg4]))
    except Exception:
        pass

    # Show error message
    QtWidgets.QMessageBox.critical(None, 'Exception Occurred!', f'{msg1}\n{msg2}\n\n{msg3}\n{msg4}')


class MainWidget(QtWidgets.QWidget):
    """
    The real main window. The other is an imposter!
    """
    def __init__(self, parent):
        super().__init__(parent)

        # Console
        self.console = Console(self)

        # Playlist
        self.plist = Playlist(self)

        # Start button
        self.startButton = QtWidgets.QPushButton('START', self)
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(lambda: parent.runThread(False))

        # Set the layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.console, 0, 0)
        L.addWidget(self.plist, 0, 1)
        L.addWidget(self.startButton, 1, 0, 1, 2)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Fuck you for not letting me set a layout as main widget.
        """
        super().__init__()

        # Create the menubar
        self.createMenubar()

        # Set the main widget
        self.setCentralWidget(MainWidget(self))

        # Set window title and show the window
        self.setWindowTitle('GimmeMusic')
        self.show()

        # Own data
        self.modulelist = {}

        # Load config
        self.config = configparser.ConfigParser()
        readconfig(self.config)

        # Default thread and worker
        self.thread = None
        self.worker = None

        # Run scanner
        self.runThread(True)

    def createMenubar(self):
        """
        Sets up the menubar
        """
        bar = self.menuBar()

        # File Menu
        file = bar.addMenu('File')
        file.addAction('Options', self.openSettings)
        file.addAction('Exit', self.close)

    def openSettings(self):
        if self.thread and self.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'AngerList On Air!', 'You can\'t interrupt AngerList while he\'s live. Please wait for the task to finish first.')
        else:
            Settings(self).exec()

    def runThread(self, isScan: bool):
        # Setup thread and worker
        self.thread = QtCore.QThread()
        if isScan:
            self.worker = PluginScanner()
        else:
            self.worker = SongScraper(self.modulelist)

        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Run event
        self.thread.started.connect(self.worker.run)

        # End events
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Worker-specific events
        self.worker.textappended.connect(lambda x: self.printline(x))
        if isScan:
            self.thread.finished.connect(self.endPluginScan)
            self.worker.pluginfound.connect(lambda x: self.addPlugin(x))
        else:
            self.thread.finished.connect(self.endScraping)

        # Start the thread!
        self.thread.start()

    def printline(self, text: str):
        self.centralWidget().console.textinput.append(text)

    def addPlugin(self, plugin: Plugin):
        # Add the plugin to the module list if it doesn't exist yet
        if plugin.modname not in self.modulelist:
            self.modulelist[plugin.modname] = plugin
            printlineInternal(self, 'Found plugin', f'{plugin.modname}.py!')

            # Check if it's already in the config
            if plugin.modname in self.config['Plugins']:
                plugin.enabled = self.config.getboolean('Plugins', plugin.modname)

                # Enable eventual genres
                for genre in plugin.genres:
                    confkey = f'{plugin.modname}_{genre}'
                    plugin.genres[genre] = self.config.getboolean('Plugins', confkey)

    def endPluginScan(self):
        # Enable the start button
        foundplugins = bool(self.modulelist)
        self.centralWidget().startButton.setEnabled(foundplugins)

        # Print scan result
        printlineInternal(self, 'Scan completed!' if foundplugins else 'No plugins found!')

        # Unset thread and worker
        self.thread = None
        self.worker = None

    def endScraping(self):
        # Print scan result
        foundsongs = bool(self.centralWidget().plist.tree.topLevelItemCount())
        printlineInternal(self, 'Scrape completed!' if foundsongs else 'No songs found!')

        # Unset thread and worker
        self.thread = None
        self.worker = None

    def closeEvent(self, e: QtGui.QCloseEvent):
        # Update config
        writeconfig(self.config, self.modulelist)

        # Original closeEvent
        super().closeEvent(e)


def main():

    # Add module folder so that we can import plugins from there
    sys.path.append(globalz.modulefolder)

    # Start the application
    app = QtWidgets.QApplication([])

    # Override the exception handler with ours
    # We must do this after the QApplication is started since it's needed to display the message box
    sys.excepthook = excepthook

    # Set up the log buffer
    globalz.logbuffer = StringIO();

    # Run the app
    mw = MainWindow()
    ret = app.exec()

    # Close the log buffer
    globalz.logbuffer.close()

    # Quit the process
    sys.exit(ret)


if __name__ == '__main__':
    main()
