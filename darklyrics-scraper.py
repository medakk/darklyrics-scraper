#!/usr/bin/python3
# dark-scraper.py

# Downloads the lyrics for all the songs in a darklyrics page
# for an artist.
# Usage: dark-scraper.py <url to artist page> [<output file>]
# or:    dark-scraper.py <artist name>        [<output file>]

import sys
import re
import threading
from urllib.request import urlopen
from queue import PriorityQueue

from bs4 import BeautifulSoup

if len(sys.argv) != 3 and len(sys.argv) != 2:
    print('Usage: {} <URL to artist page> [<output file>]'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

# Thread-safe print function
__print_lock = threading.Lock()
__p = print
def print(*args, **kwargs):
    with __print_lock:
        __p(*args, **kwargs)

def scrape_from_html(album_html):
    """
    Given a string containing the html of an album, scrape
    the lyrics from it
    """
    soup = BeautifulSoup(album_html, 'html.parser')
    header = soup.find('h2').get_text()
    content = soup.find('div', class_='lyrics')

    thanks = content.find('div', class_='thanks')
    if thanks:
        thanks.decompose()

    note = content.find('div', class_='note')
    if note:
        note.decompose()

    #get rid of the 'ARTIST LYRICS' thing
    regex = re.compile(r'[A-Z ]*LYRICS')
    blocks = regex.split(content.get_text())

    text = '*'*(len(header)+4)
    text = text + '\n' + '* '+header+' *'
    text = text + '\n' + '*'*(len(header)+4)

    for block in blocks:
        text = text + '\n' + block

    return text

# called by each thread
def get_url(q, url, index):
    print('Scraping: {}'.format(url), file=sys.stderr)
    try:
        album_html = urlopen(url).read().decode('utf-8')
        q.put((index, album_html))
    except Exception as e:
        print('get_url: Error in page: {}\n{}'.format(url, e), file=sys.stderr)

def main():
    # Figure out the URL to use
    source_arg = sys.argv[1]
    if source_arg.startswith('http://'):
        url = source_arg
    elif source_arg.startswith('www.'):
        url = 'http://'+source_arg
    elif source_arg.startswith('darklyrics.com'):
        url = 'http://www.'+source_arg
    else:
        source_arg = source_arg.lower().replace(' ', '')
        url = 'http://www.darklyrics.com/{}/{}.html'.format(source_arg[0], source_arg)

    # Read artist page
    print('Accessing {}'.format(url), file=sys.stderr)

    with urlopen(url) as ufd:
        artist_html = ufd.read().decode('utf-8')

    artist_re = re.compile(r'".*#1"')
    artist_mo = artist_re.findall(artist_html)

    album_urls = [s.replace('..', 'http://www.darklyrics.com')[1:-3] for s in artist_mo]

    # Create threads to download and scrape each page
    q = PriorityQueue()
    threads = []
    for i, url in enumerate(album_urls):
        thread = threading.Thread(target=get_url, args=(q, url, i))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Wait for all urls to download
    for thread in threads:
        thread.join()

    # File to store output in
    file_name = None
    if len(sys.argv) == 2:
        artist_soup = BeautifulSoup(artist_html, "html.parser")
        file_name = artist_soup.find("title").get_text() + ".txt"
    else:
        file_name = sys.argv[2]
    fd = open(file_name, "w")

    # Go through the queue
    while not q.empty():
        try:
            index, album_html = q.get()
            text = scrape_from_html(album_html)
            print(text, file=fd)
        except Exception as e:
            print("Error scraping from html: {}".format(album_html), file=sys.stderr)
            print(e, file=sys.stderr)


    fd.close()

if __name__ == '__main__':
    main()
