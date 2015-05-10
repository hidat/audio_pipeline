__author__ = 'cephalopodblue'
import musicbrainzngs as ngs

#####
# == Get Release
# Retrieves a raw release from MusicBrainz using their API
#####
def get_release(release_id):
    ngs.set_useragent("hidat_audio_pipeline", "0.1")
    include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels"]
    mb_release = ngs.get_release_by_id(release_id, includes=include)['release']
    return mb_release

#####
# == Process Release
# Pulls out the release information that we are interested in from the raw MusicBrainz release
#####
def process_release(mb_release, discnum):
    disc_index = discnum - 1
    release_info = {}
    release_info["release_id"] = mb_release['id']
    release_info["disc_num"] = discnum
    release_info["disc_count"] = len(mb_release["medium-list"])
    release_info["release-title"] = mb_release['title']
    rg = mb_release['release-group']
    release_info["release_group_id"] = rg['id']
    release_info["first_release_date"] = rg['first-release-date']
    if 'tag-list' in rg:
        release_info['tags'] = rg['tag-list']
    else:
        release_info['tags'] = []

    if ('title' in mb_release["medium-list"][disc_index]):
        release_info["disc-title"] = mb_release["medium-list"][disc_index]['title']

    release_info["artist-credit"] = mb_release['artist-credit']
    if ("disambiguation" in mb_release):
        release_info["disambiguation"] = mb_release['disambiguation']
    else:
        release_info["disambiguation"] = ''
    if ("label-info-list" in mb_release):
        release_info["labels"] = mb_release["label-info-list"]
    if ("date" in mb_release):
        release_info["date"] = mb_release['date']
    else:
        release_info["date"] = ""
    if ("country" in mb_release):
        release_info["country"] = mb_release['country']
    else:
        release_info["country"] = ""
    if ("barcode" in mb_release):
        release_info["barcode"] = mb_release['barcode']
    else:
        release_info["barcode"] = ""
    if ("asin" in mb_release):
        release_info["asin"] = mb_release['asin']
    else:
        release_info["asin"] = ""
    if ("packaging" in mb_release):
        release_info["packaging"] = mb_release['packaging']
    else:
        release_info["packaging"] = ""


    return release_info

def process_track(mb_release, discnum, tracknum):
    """
    Queries musicbrainz for metadata about track and release

    :param mbid: Musicbrainz id of the album
    :param tracknum: The track number
    :param discnum: The disc number of the track
    :param cached_releases: A little cache thing so that we only query once for each release
    :return: (curr, release_info, track_info) : the cache, the release metadata, the track metadata
    """

    disc_index = discnum - 1

    track = mb_release["medium-list"][disc_index]["track-list"][tracknum]
    track_info = {}
    track_info["track_num"] = tracknum
    track_info["track_count"] = len(mb_release["medium-list"][disc_index]["track-list"])
    track_info["release_track_id"] = track["id"]
    track_info["track_id"] = track["recording"]["id"]
    track_info["title"] = track["recording"]["title"]
    track_info["length"] = track["recording"]["length"]
    if ("isrc-list" in track["recording"]):
        track_info["isrcs"] = track["recording"]["isrc-list"]
    track_info["artist-credit"] = track["artist-credit"]

    return track_info