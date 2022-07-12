#!/usr/bin/env python3

# modules/soundcloud.py
# SoundCloud User scraper

import os
import re
from qtpy import QtCore
from qtpy.QtCore import Qt

from common import openURL, printline, verifyDate, getAbsPath
from plugin import Plugin
from scraping import Song, SongScraper

# Metadata
gimmeplugin = {'name': 'SoundCloud',
                 'author': 'CLF78',
                 'version': '1.0',
                 'description': 'Stream and listen to music online for free.\n<i>NOTE: Requires filling the "userlist" variable inside the plugin.</i>'}

# Core URLs
homeurl='https://soundcloud.com'
apiurl='https://api-v2.soundcloud.com'
downloadurl='https://visoundcloud.com/ajax.php'
userlistpath = getAbsPath('soundcloudusers.txt')


# Find download link using an external website
def downloadSong(scraper: SongScraper, url: str) -> str:
    printline(scraper, 'Finding download link...')
    response = openURL(scraper, 'post', downloadurl, params={'url': url})
    if response:
        printline(scraper, 'Found!')
        return response.json()['url']
    return ''


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
        url = downloadSong(scraper, track['permalink_url'])
        if url:
            scraper.songfound.emit(Song(name=track['title'], artist=track['user']['username'], genre=track['genre'], audiourl=url), 'SoundCloud')

    # If we reach the end of the loop, call this function again with a different offset
    lastdate = track['created_at']
    scrapeUser(scraper, userid, client_id, lastdate)


# Locate user ID
def findUserID(scraper: SongScraper, username: str, client_id: str) -> str:

    # Initialize to empty string
    userid = ''

    # Get the user id by executing a search query for the username
    # Not my proudest solution, but it does the job without requiring an API key (which SC doesn't even provide)
    params = {'q': username, 'client_id': client_id, 'limit': 1}
    searchresults = openURL(scraper, 'get', f'{apiurl}/search', params=params)
    if searchresults:

        # Make sure the result matches the username given
        json = searchresults.json()
        if json['total_results'] and json['collection'][0]['permalink_url'].split('/')[-1] == username:
            userid = json['collection'][0]['urn'].split(':')[2]
            printline(scraper, 'Found userid:', userid)
        else:
            printline(scraper, 'Username', username, 'not found!')

    # Return the ID
    return userid


# Main scraping function
def scrapeMain(scraper: SongScraper, moduledata: Plugin) -> None:

    # Initialize variables
    client_id = ''

    # Check if the userlist is valid
    if not os.path.isfile(userlistpath):
        printline(scraper, 'User list not found!')
        return

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

    # Open the user list
    with open(userlistpath) as f:
        userlist = f.read().splitlines()

    # Parse each user
    for user in userlist:
        if user:
            printline(scraper, 'Processing user', user + '...')
            userid = findUserID(scraper, user, client_id)
            if userid:
                scrapeUser(scraper, userid, client_id)
            else:
                printline(scraper, 'Invalid user list entry', user)


if __name__ == '__main__':
    print("Run main.py to access the program!")
