#!/usr/bin/python3
# dark-scraper.py

# Downloads the lyrics for all the songs in a darklyrics page
# for an artist.
# Usage: dark-scraper.py <url to artist page> <output file>

# TODO: Handle exceptions

import sys
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen

if len(sys.argv)!=3 and len(sys.argv)!=2:
    print("Usage: {} <URL to artist page> <output file>".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

url = sys.argv[1]

with urlopen(url) as ufd:
    artist_html = ufd.read().decode("utf-8")

artist_re = re.compile(r'".*#1"')
artist_mo = artist_re.findall(artist_html)

album_urls = [s.replace("..", "http://www.darklyrics.com")[1:-3] for s in artist_mo]

file_name=None
if len(sys.argv)==2:
    artist_soup = BeautifulSoup(artist_html, "html.parser")
    file_name = artist_soup.find("title").get_text() + ".txt"
else:
    file_name = sys.argv[2]

fd = open(file_name, "w")

for url in album_urls:
    print("Scraping: " + url)
    with urlopen(url) as ufd:
        album_html = ufd.read()

    soup = BeautifulSoup(album_html, "html.parser")

    header = soup.find("h2").get_text()

    content = soup.find("div", class_="lyrics")
    content.find("div", class_="thanks").decompose()
    content.find("div", class_="note").decompose()

    #get rid of the "ARTIST LYRICS" thing
    regex = re.compile(r'[A-Z ]*LYRICS')
    text = regex.split(content.get_text())

    print("*"*(len(header)+4), file=fd)
    print("* "+header+" *", file=fd)
    print("*"*(len(header)+4), file=fd)

    for block in text:
        fd.write(block)

fd.close()
