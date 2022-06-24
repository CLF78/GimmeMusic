#!/usr/bin/env python3

# globalz.py
# This file defines globals to be used by GimmeMusic.
# NOTE: Do NOT include this in plugins!

import os

# HTML parser for BeautifulSoup
htmlparser = 'html.parser'

# Log buffer for printing
logbuffer = None

# Date for scraping and settings
lastuse = None

# Files/folders
path = os.path.dirname(os.path.abspath(__file__))
logfile = os.path.join(path, 'log.txt')
configfile = os.path.join(path, 'config.ini')
modulefolder = os.path.join(path, 'modules')

# Variables
pluginmeta = 'gimmeplugin'
mainfunc = 'scrapeMain'

if __name__ == '__main__':
    print("Run main.py to access the program!")
