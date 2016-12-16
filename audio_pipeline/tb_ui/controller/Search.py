import urllib.parse
import webbrowser
import tempfile
import os
import time
import re

whitespace = re.compile("\s")
mb_release = "http://musicbrainz.org/add"
albunack_search_url = "http://www.albunack.net/artist/search?"
albunack_search_terms = {"artistname": "", "musicbrainzartistid": "", "musicbrainzartistdbid": "", "discogsartistid": ""}
mb_search_url = "http://musicbrainz.org/search?query="

mb_search_terms = {"type": "", "method": "advanced"}

forbidden = [":", "!", "\"", "+", "&"]


def albunack_search(track, artist=None):
    """
    Given an audiofile, open an albunack artist search in the browser
    :param self:
    :param track:
    :return:
    """
    search_terms = None
    if artist:
        search_terms = albunack_search_terms.copy()
        search_terms["artistname"] = artist
    elif track.artist.value:
        search_terms = albunack_search_terms.copy()
        search_terms["artistname"] = track.album_artist.value
    if search_terms:
        search_terms = urllib.parse.urlencode(search_terms)
        search_url = albunack_search_url + search_terms
        print(search_url)
        webbrowser.open(search_url)


def mb_search(track, artist=None, barcode=None, barcode_value=None):
    """
    Given an audiofile, open an MB search in the browser

    search priorities:
        barcode and/or catalog number
        release name and/or artist name
    :param self:
    :param track:
    :return:
    """
    query = []
    if barcode:
        search_terms = mb_search_terms.copy()
        search_terms["type"] = "release"

        if barcode_value:
            query.append(("barcode", barcode_value))
            query.append(("catno", barcode_value))
        else:
            if track.barcode.value:
                query.append(("barcode", track.barcode.value))
            if track.catalog_num.value:
                query.append(("catno", track.catalog_num.value))
    elif artist:
        search_terms = mb_search_terms.copy()
        search_terms["type"] = "artist"

        query.append((artist,))
    else:
        search_terms = mb_search_terms.copy()
        if track.album.value:
            search_terms["type"] = "release"
            query.append((track.album.value,))
            if track.album_artist.value:
                query.append(("artist", track.album_artist.value))
        else:
            search_terms["type"] = "artist"
            if track.album_artist.value:
                query.append((track.album_artist.value,))

    if search_terms and len(query) > 0:
        query = prep_query(query)
        search_terms = urllib.parse.urlencode(search_terms)
        search_url = "%s%s&%s" % (mb_search_url, query, search_terms)
        print(search_url)
        webbrowser.open(search_url)
        
        
def mb_release_seed(release_seed):
    fd, fname = tempfile.mkstemp(suffix = '.html')
    os.close(fd)
    with open(fname, "wb") as f:
        f.write(release_seed.encode('utf-8'))
    webbrowser.open(fname)
    return fname


def prep_query(query):
    prepped_query = []
    for part in query:
        if len(part) > 1:
            q = "%s:\"%s\"" % (part[0], part[1])
        else:
            q = part[0]
        q = urllib.parse.quote_plus(q)
        prepped_query.append(q)
        print(prepped_query)

    return " ".join(prepped_query)