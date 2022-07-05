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
cachedir = os.path.join(path, '.web_cache')

# Variables
pluginmeta = 'gimmeplugin'
mainfunc = 'scrapeMain'
defaultUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.68'


if __name__ == '__main__':
    print("Run main.py to access the program!")
