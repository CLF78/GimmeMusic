"""
Globals to be used by the program.
NOTE: Do NOT include this in plugins!
"""

import os

# HTML parser for BeautifulSoup
htmlparser = 'html.parser'

# Log buffer for printing
logbuffer = None

# Files/folders
path = os.path.dirname(os.path.abspath(__file__))
logfile = os.path.join(path, 'log.txt')
configfile = os.path.join(path, 'config.ini')
modulefolder = os.path.join(path, 'modules')

# Variables
pluginmeta = 'angerlistdata'
mainfunc = 'scrapeMain'
