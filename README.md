## GimmeMusic
GimmeMusic is a GUI scraper written in Python, whose goal is to collect the latest music releases from various websites (through configurable plugins). After scraping, the user can filter/edit the results and export them to a M3U playlist, ready for use in programs like VLC or mpv. The program is intended for power users.

## How To Use
* Install [Python 3.7 (or newer)](http://www.python.org)
* Install one of the 4 Qt backends:
    - [PyQt5 5.9.0 (or newer, recommended)](https://pypi.org/project/PyQt5/)
    - [PySide2 5.12.0 (or newer)](https://pypi.org/project/PySide2/)
    - [PyQt6 6.2.0 (or newer)](https://pypi.org/project/PyQt6/)
    - [PySide6 6.2.0 (or newer)](https://pypi.org/project/PySide6/)
* Install the remaining dependencies through `pip` using `requirements.txt` ([Guide](https://pip.pypa.io/en/latest/user_guide/#requirements-files))
* Execute the command `python3 main.py` from the program's folder.

## Implemented Plugins
The currently implemented plugins are websites that the author is personally interested in, but more may eventually be added:
* Beatport
* Hardstyle.com
* HardTunes
* JunoDownload
* SoundCloud (needs improvements)

# Planned Plugins
* Bandcamp
* YouTube
* ...more? Feel free to submit any plugin or request for one!
