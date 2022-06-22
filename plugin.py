import importlib
import os
import sys
import types

from qtpy import QtCore

import globalz
from common import printline

def deleteModule(module: object, modName: str):
    """
    Simple helper to delete a module.
    Use the return value to delete the last reference to the module.
    """
    del sys.modules[modName]
    del module
    return None

class Plugin:
    def __init__(self, name: str, module: object, modname: str):
        self.name = name
        self.genres = {}
        self.author = ''
        self.version = ''
        self.description = ''
        self.module = module
        self.modname = modname
        self.enabled = True


class PluginScanner(QtCore.QObject):
    finished = QtCore.Signal()
    textappended = QtCore.Signal(str)
    pluginfound = QtCore.Signal(Plugin)

    def run(self):
        """
        The main function
        """
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
            try:
                if file[0] in sys.modules:
                    module = sys.modules[file[0]]
                else:
                    module = importlib.import_module(file[0])
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
            if not isinstance(func, types.FunctionType):
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
