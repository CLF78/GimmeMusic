#!/usr/bin/env python3

# modules/soundcloud.py
# SoundCloud User scraper

import os
import re
from qtpy import QtCore
from qtpy.QtCore import Qt

from common import getAbsPath, openURL, printline, verifyDate
from plugin import Plugin, PluginScanner
from scraping import Song, SongScraper

# Metadata
gimmeplugin = {'name': 'SoundCloud',
                 'author': 'CLF78',
                 'version': '2.0',
                 'description': 'Stream and listen to music online for free.\n<i>NOTE: Add users you want to check to the file "soundcloudusers.txt" in the "modules" folder.</i>'}

# Core URLs
homeurl='https://soundcloud.com'
apiurl='https://api-v2.soundcloud.com'
userlistpath = getAbsPath('soundcloudusers.txt')

# Individual user scraping function
def scrapeUser(scraper: SongScraper, userid: str, client_id: str, offset: str = '0') -> None:

    # Get the latest 20 entries
    params = {'client_id': client_id, 'limit': 20, 'offset': offset}
    usertracks = openURL(scraper, 'get', f'{apiurl}/users/{userid}/tracks', params=params)
    if not usertracks:
        return

    # Get the tracks
    usertracks = usertracks.json()['collection']
    printline(scraper, 'Processing', len(usertracks), 'tracks...')
    for track in usertracks:

        # Verify timestamp
        date = QtCore.QDate.fromString(track['created_at'], Qt.ISODate)
        if not verifyDate(date):
            printline(scraper, 'Reached max delta date. Moving on...')
            return

        # Skip tracks longer than 15 minutes
        if track['duration'] > 900000:
            continue

        # Find the direct download link. If found, append the track to the list
        scraper.songfound.emit(Song(name=track['title'], artist=track['user']['username'], genre=track['genre'], audiourl=track['permalink_url']), 'SoundCloud')

    # If we reach the end of the loop, call this function again with a different offset
    lastdate = track['created_at']
    scrapeUser(scraper, userid, client_id, lastdate)


# Locate user ID
def findUserID(scraper: SongScraper, username: str, client_id: str) -> str:

    # Initialize to empty string
    userid = ''

    # Get the user id by executing a search query for the username
    # Not my proudest solution, but it does the job without requiring an API key (which SC doesn't even provide)
    params = {'q': username, 'client_id': client_id, 'limit': 20}
    searchresults = openURL(scraper, 'get', f'{apiurl}/search/users', params=params)
    if searchresults:

        # Make sure the result matches the username given
        json = searchresults.json()
        if json['total_results']:
            for entry in json['collection']:
                if entry['permalink_url'].split('/')[-1] == username:
                    userid = entry['urn'].split(':')[2]
                    break

    # Return the ID
    if userid:
        printline(scraper, 'Found userid:', userid)
    else:
        printline(scraper, 'Username', username, 'not found!')
    return userid


# Main scraping function
def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Initialize variables
    client_id = ''

    # To make API calls, we need a client ID. Therefore, download the main page
    printline(scraper, 'Requesting Client ID...')
    homePage = openURL(scraper, 'get', homeurl, clearcookies=True)
    if homePage:

        # The ID is hidden in one of the linked JS files. Code copied and modified from youtube-dl
        # The list is parsed in reverse as the relevant files are usually at the bottom of the HTML
        for src in reversed(re.findall(r'<script[^>]+src="([^"]+)"', homePage.text)):
            script = openURL(scraper, 'get', src)
            if script:

                # Find the first match and sanitize it
                matches = re.search(r'client_id\s*:\s*"([0-9a-zA-Z]{32})"', script.text)
                if matches:
                    client_id = matches.group()[11:-1]
                    printline(scraper, 'Found Client ID:', client_id)
                    break

    # If the client id was not found, return immediately
    if not client_id:
        printline(scraper, 'Could not find Client ID! Bailing...')
        return

    # Parse each user
    for user, enabled in moduledata.genres.items():
        if enabled:
            printline(scraper, 'Processing user', user + '...')
            userid = findUserID(scraper, user, client_id)
            if userid:
                scrapeUser(scraper, userid, client_id)
            else:
                printline(scraper, 'Invalid user list entry', user)


def scanMain(scanner: PluginScanner, moduledata: Plugin):

    # Check if the user list exists
    if not os.path.isfile(userlistpath):
        printline(scanner, 'User list not found!')
        return False

    # Open it
    with open(userlistpath) as f:
        users = f.read().splitlines()

    # Add each valid line as a genre (default to enabled)
    for user in users:
        if user:
            moduledata.genres[user] = True

    # If the resulting list is empty, do not load the plugin
    return bool(moduledata.genres)


if __name__ == '__main__':
    print("Run main.py to access the program!")
