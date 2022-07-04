#!/usr/bin/env python3

# main.py
# This is the main executable for GimmeMusic.

# TODO allow clearing the request cache

# Python version check
# Currently, QtPy only supports Python 3.7+, so we follow suit
import sys
if sys.version_info < (3, 7):
    raise Exception('Please update your copy of Python to 3.7 or greater. Currently running on: ' + sys.version.split()[0])

# Standard imports
import traceback
from io import StringIO

# If any other error occurs, let QtPy throw its own exceptions without intervention
try:
    from qtpy import QtCore, QtGui, QtWidgets
    from qtpy.QtCore import Qt
except ImportError:
    raise Exception('QtPy is not installed in this Python environment. Go online and download it.')

try:
    import requests
except ImportError:
    raise Exception('requests is not installed in this Python environment. Go online and download it.')

try:
    import cachecontrol
except ImportError:
    raise Exception('cachecontrol is not installed in this Python environment. Go online and download it.')

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
    from scraping import SongScraper
    from settings import Settings, readconfig, writeconfig
except ImportError:
    raise Exception("One or more program components are missing! Quitting...")


def excepthook(*exc_info):
    """
    Custom unhandled exceptions handler
    """
    # Strings
    separator = '-' * 80
    timeString = QtCore.QDateTime.currentDateTime().toString(Qt.ISODate)
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
        self.splitter = QtWidgets.QSplitter(self)

        # Console
        self.console = Console(self.splitter)

        # Playlist
        self.plist = Playlist(self.splitter)

        # Start button
        self.startButton = QtWidgets.QPushButton('START', self)
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(self.handleStartButton)

        # Set the layout
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(self.splitter)
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

        # Initialize the module list
        self.modulelist = {}

        # Initialize thread and worker
        self.thread = None
        self.worker = None

        # Load config
        self.config = QtCore.QSettings(globalz.configfile, QtCore.QSettings.IniFormat, self)
        self.config.setFallbacksEnabled(False)
        readconfig(self.config)

        # Create the menubar
        self.createMenubar()

        # Set the main widget
        self.setCentralWidget(MainWidget(self))

        # Set window title
        self.setWindowTitle('GimmeMusic')

        # Reload state
        placeholder = QtCore.QByteArray()
        geometry = self.config.value('WindowSettings/mwgeometry', placeholder)
        state = self.config.value('WindowSettings/mwstate', placeholder)
        splitterstate = self.config.value("WindowSettings/splitterstate", placeholder)
        if not geometry.isEmpty():
            self.restoreGeometry(geometry)
        if not state.isEmpty():
            self.restoreState(state)
        if not splitterstate.isEmpty():
            self.centralWidget().splitter.restoreState(splitterstate)

        # Show the window
        self.show()

        # Attempt to import lxml
        try:
            import lxml
            globalz.htmlparser = 'lxml'
        except ImportError:
            printline('lxml not found, falling back to html.parser...')

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
            self.centralWidget().plist.tree.setSortingEnabled(False)

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

            # Enable it if the config says so
            plugin.enabled = self.config.value(f'Plugins/{plugin.modname}', 'false') == 'true'
            if plugin.genres:
                for genre in plugin.genres:
                    confkey = f'{plugin.modname}_{genre}'
                    plugin.genres[genre] = self.config.value(f'Plugins/{confkey}', 'false') == 'true'


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
        plist = self.centralWidget().plist
        plist.tree.setSortingEnabled(True)

        # Update buttons
        plist.updateButtons()

        # Unset thread and worker
        self.thread = None
        self.worker = None

    def closeEvent(self, e: QtGui.QCloseEvent):
        """
        Override the close event to prevent closing during a task (or to save the configuration if none is running).
        """
        if self.thread and self.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'Task Running!', 'Please stop the task or wait for it to finish first.')
            e.ignore()
        else:
            writeconfig(self.config, self.modulelist, self.saveGeometry(), self.saveState(), self.centralWidget().splitter.saveState())
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
