#!/usr/bin/env python3

# common.py
# This file contains several functions that can be called by GimmeMusic plugins or the program itself.

from bs4 import BeautifulSoup
import requests

import globalz


def getMainWindow(self):
    """
    Gets the main window from the current widget.
    """
    parent = self.parent()
    if parent is None:
        return self
    return getMainWindow(parent)


def printline(self, *args, **kwargs):
    """
    Prints text to the console.
    """
    # Sanity check
    if not self:
        return

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


def openURL(self, method: str, url: str, session: requests.Session = None, **kwargs):
    """
    Requests wrapper for plugin use.
    """
    # URL sanity check
    if not url:
        printline(self, 'Missing URL!')
        return None

    # Try opening the url, catching any error
    try:
        printline(self, f'Connecting to <i>{url}</i>...')

        # Get the page with a maximum time of 10 seconds
        if session:
            r = session.request(method.upper(), url, timeout=10, **kwargs)
        else:
            r = requests.request(method.upper(), url, timeout=10, **kwargs)

        # Raise an error if the status code is an error one
        r.raise_for_status()
        return r

    except Exception as e:
        printline(self, 'An exception occurred while retrieving the page:', e)
        return None


def getWebPage(self, r):
    """
    BeautifulSoup wrapper for plugin use.
    """
    # Sanity check
    if not r:
        printline(self, 'Response is empty!')
        return

    # Attempt to parse the page
    try:
        return BeautifulSoup(r.content, globalz.htmlparser)
    except:
        printline(self, 'Failed to parse webpage!')
        return None


if __name__ == '__main__':
    print("Run main.py to access the program!")
