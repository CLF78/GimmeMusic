#!/usr/bin/env python3

# main.py
# This is the main executable for GimmeMusic.

# TODO song found event
# TODO improve playlist columns

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
    from common import getMainWindow, printline
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
    The main widget, containing the console and the playlist.
    """
    def __init__(self, parent):
        super().__init__(parent)

        # Splitter
        splitter = QtWidgets.QSplitter(self)

        # Console
        self.console = Console(splitter)

        # Playlist
        self.plist = Playlist(splitter)

        # Start button
        self.startButton = QtWidgets.QPushButton('START', self)
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(self.handleStartButton)

        # Set the layout
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(splitter)
        L.addWidget(self.startButton)

    def handleStartButton(self):
        mw = getMainWindow(self)
        if mw.thread and mw.thread.isRunning():
            printline(mw, "Terminating scrape...")
            mw.stopscrape.emit()
        else:
            self.startButton.setText('STOP')
            mw.runThread(False)


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window. Exciting stuff.
    """
    stopscrape = QtCore.Signal()

    def __init__(self):
        super().__init__()

        # Create the menubar
        self.createMenubar()

        # Set the main widget
        self.setCentralWidget(MainWidget(self))

        # Set window title and show the window
        self.setWindowTitle('GimmeMusic')
        self.show()

        # Initialize the module list
        self.modulelist = {}

        # Initialize thread and worker
        self.thread = None
        self.worker = None

        # Attempt to import lxml
        try:
            import lxml
            globalz.htmlparser = 'lxml'
        except ImportError:
            printline('lxml not found, falling back to html.parser...')

        # Load config
        self.config = configparser.ConfigParser()
        readconfig(self.config)

        # Run the plugin scanner
        self.runThread(True)

    def createMenubar(self):
        """
        Sets up the menubar, unsurprisingly.
        """
        bar = self.menuBar()

        # File Menu
        file = bar.addMenu('File')
        preficon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView)
        closeicon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogCancelButton)
        file.addAction(preficon ,'Preferences', self.openSettings, 'CTRL+P')
        file.addAction(closeicon, 'Exit', self.close, 'CTRL+Q')

    def openSettings(self):
        """
        Opens the settings if a secondary thread isn't running.
        """
        if self.thread and self.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'Task Running!', 'Please stop the task or wait for it to finish first.')
        else:
            Settings(self).exec()

    def runThread(self, isScan: bool):
        """
        Runs either the plugin scanner or the scraper, depending on the bool.
        """
        self.thread = QtCore.QThread(self)
        if isScan:
            self.worker = PluginScanner()
        else:
            self.worker = SongScraper(self)

        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Run event
        self.thread.started.connect(self.worker.run)

        # End events
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Worker-specific events
        self.worker.textappended.connect(self.centralWidget().console.textinput.append)
        if isScan:
            self.worker.pluginfound.connect(self.addPlugin)
            self.thread.finished.connect(self.endPluginScan)
        else:
            self.worker.songfound.connect(self.centralWidget().plist.addEntry)
            self.thread.finished.connect(self.endScraping)

        # Start the thread!
        self.thread.start()

    def addPlugin(self, plugin: Plugin):
        """
        Adds a plugin to the dictionary and parses the corresponding config entries.
        """
        if plugin.modname not in self.modulelist:
            self.modulelist[plugin.modname] = plugin
            printline(self, 'Found plugin', f'{plugin.modname}.py!')

            # Enable it (with sanitized input)
            try:
                plugin.enabled = self.config.getboolean('Plugins', plugin.modname, fallback=False)
            except ValueError:
                plugin.enabled = False

            # Enable genres if specified (with sanitized input)
            for genre in plugin.genres:
                confkey = f'{plugin.modname}_{genre}'
                try:
                    plugin.genres[genre] = self.config.getboolean('Plugins', confkey, fallback=False)
                except ValueError:
                    plugin.genres[genre] = False

    def endPluginScan(self):
        """
        Enables the start button and ends the scan.
        """
        foundplugins = bool(self.modulelist)
        self.centralWidget().startButton.setEnabled(foundplugins)
        printline(self, 'Scan completed!' if foundplugins else 'No plugins found!')

        # Unset thread and worker
        self.thread = None
        self.worker = None

    def endScraping(self):
        """
        Resets the start button and ends the scrape.
        """
        self.centralWidget().startButton.setText('START')

        # Print scan result
        foundsongs = bool(self.centralWidget().plist.tree.topLevelItemCount())
        printline(self, 'Scrape completed!' if foundsongs else 'No songs found!')

        # Enable sorting the tree
        tree = self.centralWidget().plist.tree.setSortingEnabled(True)

        # Unset thread and worker
        self.thread = None
        self.worker = None

    def closeEvent(self, e: QtGui.QCloseEvent):
        """
        Override the close event to prevent closing during a task and to save the configuration.
        """
        if self.thread and self.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'Task Running!', 'Please stop the task or wait for it to finish first.')
            e.ignore()
        else:
            writeconfig(self.config, self.modulelist)
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
    globalz.logbuffer = StringIO()

    # Run the app
    mw = MainWindow()
    ret = app.exec()

    # Close the log buffer
    globalz.logbuffer.close()

    # Quit the process
    sys.exit(ret)


if __name__ == '__main__':
    main()
