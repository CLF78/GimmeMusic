"""
Fuck globals, all my homies hate globals
"""

import os

# Files/folders
path = os.path.dirname(os.path.abspath(__file__))
logfile = os.path.join(path, 'log.txt')
configfile = os.path.join(path, 'config.ini')
modulefolder = os.path.join(path, 'modules')

# Variables
pluginmeta = 'angerlistdata'
mainfunc = 'scrapeMain'
