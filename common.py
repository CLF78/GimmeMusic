# common.py
# This contains several functions that can be called from plugins or the program itself

import sys


def getMainWindow(self):
    """
    Gets the main window from the current widget
    """
    parent = self.parent()
    if parent is None:
        return self
    return getMainWindow(parent)


def printlineInternal(self, *args):
    """
    Version of printline used internally by the program. DO NOT USE FOR PLUGINS!
    """
    getMainWindow(self).printline(' '.join(map(str, args)))


def deleteModule(module: object, modName: str):
    """
    Simple helper to delete a module.
    Use the return value to delete the last reference to the module.
    """
    del sys.modules[modName]
    del module
    return None
