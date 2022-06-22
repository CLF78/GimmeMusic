# common.py
# This contains several functions that can be called from plugins or the program itself

from qtpy import QtCore
import globalz

def getMainWindow(self):
    """
    Gets the main window from the current widget
    """
    parent = self.parent()
    if parent is None:
        return self
    return getMainWindow(parent)


def printline(self, *args, **kwargs):
    """
    Prints text to the console
    """

    # Empty the log buffer
    globalz.logbuffer.seek(0)
    globalz.logbuffer.truncate()

    # Print to the buffer
    print(*args, end='', file=globalz.logbuffer, **kwargs)

    # If the object calling this function has the textappended attribute, emit the signal
    if hasattr(self, 'textappended'):
        self.textappended.emit(globalz.logbuffer.getvalue())

    # Else get the main window and append the text
    else:
        getMainWindow(self).centralWidget().console.textinput.append(globalz.logbuffer.getvalue())
