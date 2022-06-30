#!/usr/bin/env python3

# plugin.py
# This file defines GimmeMusic's plugin architecture.

import importlib
import os
import sys

from qtpy import QtCore

import globalz
from common import printline


def deleteModule(module: object, modName: str) -> None:
    """
    Simple helper to delete a module.
    Use the return value to delete the last reference to the module.
    """
    del sys.modules[modName]
    del module
    return None


class Plugin:
    """
    Plugin metadata holder class.
    """
    def __init__(self, name: str, module: object, modname: str):
        self.name = name
        self.genres = {}
        self.author = ''
        self.version = ''
        self.description = ''
        self.module = module
        self.modname = modname
        self.enabled = False


class PluginScanner(QtCore.QObject):
    """
    Plugin scanner (run on a separate thread from the GUI).
    """
    finished = QtCore.Signal()
    textappended = QtCore.Signal(str)
    pluginfound = QtCore.Signal(Plugin)

    def run(self):
        printline(self, 'Initiating plugin scan...')

        # Make the modules folder in case it doesn't exist
        os.makedirs(globalz.modulefolder, exist_ok=True)

        # Get every file in the modules directory
        for file in os.listdir(globalz.modulefolder):

            # Split extension from filename
            file = os.path.splitext(file)

            # Check if it's a .py file
            if file[1] != '.py':
                continue

            # Try importing the file, skip if it fails
            # Don't reimport the module if it's already imported
            try:
                module = sys.modules.get(file[0], importlib.import_module(file[0]))
            except Exception as e:
                printline(self, 'Failed to import module', file[0] + ':', e)
                continue

            # Check if the required metadata is present
            data = getattr(module, globalz.pluginmeta, None)
            if not isinstance(data, dict) or 'name' not in data:
                printline(self, 'Module', file[0], 'is missing the required metadata!')
                module = deleteModule(module, file[0])
                continue

            # Check if the main function exists
            func = getattr(module, globalz.mainfunc, None)
            if not callable(func):
                printline(self, 'Module', file[0], 'is missing the main function!')
                module = deleteModule(module, file[0])
                continue

            # Create the plugin class
            plugin = Plugin(data['name'], module, file[0])

            # Fill in the rest of the metadata (assuming conversions to string won't fail)
            plugin.author = str(data.get('author', ''))
            plugin.version = str(data.get('version', ''))
            plugin.description = str(data.get('description', ''))

            # Genres with string failsafe
            genres = data.get('genres', [])
            if type(genres) == list:
                for genre in genres:
                    plugin.genres[str(genre)] = True

            # Emit event to save plugin
            self.pluginfound.emit(plugin)

        # Emit event when loop ends
        self.finished.emit()

if __name__ == '__main__':
    print("Run main.py to access the program!")
