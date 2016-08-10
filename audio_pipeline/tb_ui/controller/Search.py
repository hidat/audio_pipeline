import urllib.parse
import webbrowser
import re

whitespace = re.compile("\s")

albunack_search_url = "http://www.albunack.net/artist/search?"
albunack_search_terms = {"artistname": "", "musicbrainzartistid": "", "musicbrainzartistdbid": "", "discogsartistid": ""}
mb_search_url = "http://musicbrainz.org/search?query="

mb_search_terms = {"type": "", "method": "advanced"}

forbidden = [":", "!", " ", "\t"]


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


def mb_search(track, tracks=None, artist=None):
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
    if artist:
        search_terms = mb_search_terms.copy()
        search_terms["type"] = "artist"

        query.append(("artist", artist))
    else:
        search_terms = mb_search_terms.copy()
        search_terms["type"] = "release"
        if track.barcode.value:
            query.append(("barcode", track.barcode.value))
        if track.catalog_num.value:
            query.append(("catno", track.catalog_num.value))
        if len(query) == 0:
            if track.album.value:
                query.append((track.album.value,))
            if track.album_artist.value:
                query.append(("artist", track.album_artist.value))
            if tracks:
                query.append(("tracksmedium", str(tracks)))

    if search_terms and len(query) > 0:
        query = prep_query(query)
        search_terms = urllib.parse.urlencode(search_terms)
        search_url = "%s%s&%s" % (mb_search_url, query, search_terms)
        print(search_url)
        webbrowser.open(search_url)


def prep_query(query):
    prepped_query = []
    for part in query:
        if len(part) > 1:
            field = part[0]
            value = part[1]
            concat = lambda field, value:"%s:%s" %(field, value)
        else:
            field = ""
            value = part[0]
            concat = lambda field, value: value
        if whitespace.search(value):
            value = "\"" + value + "\""
        q = concat(field, value)
        for r in forbidden:
            rep = "%s%s" % ("%", hex(ord(r))[2:])
            q = q.replace(r, rep)
        prepped_query.append(q)

    return " ".join(prepped_query)