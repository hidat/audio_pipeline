__author__ = 'cephalopodblue'
import musicbrainzngs as ngs

def find_meta_release(mbid, tracknum, discnum, curr):
    """
    Queries musicbrainz for metadata about track and release

    :param mbid: Musicbrainz id of the album
    :param tracknum: The track number
    :param discnum: The disc number of the track
    :param curr: A little cache thing so that we only query once for each release
    :return: (curr, release_info, track_info) : the cache, the release metadata, the track metadata
    """
    ngs.set_useragent("hidat_audio_pipeline", "0.1")

    disc_index = discnum - 1

    if mbid not in curr:
        include=["artist-credits", "recordings", "isrcs", "media"]
        curr[mbid] = ngs.get_release_by_id(mbid, includes=include)['release']

    release = curr[mbid]
    release_info = {}
    release_info["release_id"] = mbid
    release_info["disc_num"] = discnum
    release_info["release-title"] = release['title']
    if ('title' in release["medium-list"][disc_index]):
        release_info["disc-title"] = release["medium-list"][disc_index]['title']
    release_info["artists-credit"] = release['artist-credit']
    if ("disambiguation" in release):
        release_info["disambiguation"] = release['disambiguation']
    if ("label-info-list" in release):
        release_info["label-info-list"] = release["label-info-list"]
    if ("date" in release):
        release_info["date"] = release['date']
    else:
        release_info["date"] = ""
    if ("country" in release):
        release_info["country"] = release['country']
    else:
        release_info["country"] = ""
    if ("barcode" in release):
        release_info["barcode"] = release['barcode']
    else:
        release_info["barcode"] = ""
    if ("asin" in release):
        release_info["asin"] = release['asin']
    else:
        release_info["asin"] = ""

    track = curr[mbid]["medium-list"][disc_index]["track-list"][tracknum]
    track_info = {}
    track_info["track_num"] = tracknum
    track_info["release_track_id"] = track["id"]
    track_info["track_id"] = track["recording"]["id"]
    track_info["title"] = track["recording"]["title"]
    track_info["length"] = track["recording"]["length"]
    if ("isrc-list" in track["recording"]):
        track_info["isrcs"] = track["recording"]["isrc-list"]
    track_info["artist-credits"] = track["artist-credit"]

    return curr, release_info, track_info