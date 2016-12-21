#!/usr/bin/python3
# dark-scraper.py

# Downloads the lyrics for all the songs in a darklyrics page
# for an artist.
# Usage: dark-scraper.py <url to artist page> [<output file>]
# or:    dark-scraper.py <artist name>        [<output file>]

# TODO: Handle exceptions more gracefully

import sys
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen

if len(sys.argv)!=3 and len(sys.argv)!=2:
    print("Usage: {} <URL to artist page> [<output file>]".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

# Figure out the URL to use
source_arg = sys.argv[1]
if source_arg.startswith("http://"):
    url = source_arg
elif source_arg.startswith("www."):
    url = "http://"+source_arg
elif source_arg.startswith("darklyrics.com"):
    url = "http://www."+source_arg
else:
    source_arg = source_arg.lower().replace(' ', '')
    url = "http://www.darklyrics.com/{}/{}.html".format(source_arg[0], source_arg)
print("Accessing {}".format(url), file=sys.stderr)

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
error_urls = []

for url in album_urls:
    try:
        print("Scraping: " + url, file=sys.stderr)
        with urlopen(url) as ufd:
            album_html = ufd.read()

        soup = BeautifulSoup(album_html, "html.parser")

        header = soup.find("h2").get_text()

        content = soup.find("div", class_="lyrics")
        try:
            content.find("div", class_="thanks").decompose()
        except:
            pass # no thanks found. No problem, we were trying
                 # to get rid of it anyway
        try:
            content.find("div", class_="note").decompose()
        except:
            pass # no "note" found. No problem, we were trying
                 # to get rid of it anyway

        #get rid of the "ARTIST LYRICS" thing
        regex = re.compile(r'[A-Z ]*LYRICS')
        text = regex.split(content.get_text())

        print("*"*(len(header)+4), file=fd)
        print("* "+header+" *", file=fd)
        print("*"*(len(header)+4), file=fd)

        for block in text:
            fd.write(block)
    except Exception as e:
        print("Error in page: {}".format(url), file=sys.stderr)
        print(e, file=sys.stderr)
        error_urls.append(url)

if error_urls:
    print("\nError parsing the following pages:",file=sys.stderr)
    print(*error_urls, sep='\n',file=sys.stderr)

fd.close()
