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

if len(sys.argv)!=3:
    print("Usage: {} <URL to artist page> <output file>".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

url = sys.argv[1]

with urlopen(url) as ufd:
    artist_html = ufd.read().decode("utf-8")

artist_re = re.compile(r'".*#1"')
artist_mo = artist_re.findall(artist_html)

album_urls = [s.replace("..", "http://www.darklyrics.com")[1:-3] for s in artist_mo]

fd = open(sys.argv[2], "w")

for url in album_urls:
    print(url)
    with urlopen(url) as ufd:
        album_html = ufd.read()

    soup = BeautifulSoup(album_html, "html.parser")

    header = soup.find("h2").get_text()

    content = soup.find("div", class_="lyrics")
    content.find("div", class_="thanks").decompose()
    content.find("div", class_="note").decompose()

    print(header, file=fd)
    print(content.get_text(), file=fd)
    print("", file=fd)

fd.close()
