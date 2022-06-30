#!/usr/bin/env python3

# common.py
# This file contains several functions that can be called by GimmeMusic plugins or the program itself.

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
    if hasattr(self, 'textappended') and hasattr(self.textappended, 'emit') and callable(self.textappended.emit):
        self.textappended.emit(globalz.logbuffer.getvalue())

    # Else get the main window and append the text
    else:
        getMainWindow(self).centralWidget().console.textinput.append(globalz.logbuffer.getvalue())

if __name__ == '__main__':
    print("Run main.py to access the program!")
