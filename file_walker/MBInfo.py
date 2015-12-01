__author__ = 'cephalopodblue'
import musicbrainzngs as ngs

#####
# == Get Release
# Retrieves a raw release from MusicBrainz using their API
#####
def get_release(release_id):
    ngs.set_useragent("hidat_audio_pipeline", "0.1")
    include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels", "artists"]
    mb_release = ngs.get_release_by_id(release_id, includes=include)['release']
    return mb_release

def get_artist(artist_id):
    ngs.set_useragent("hidat_audio_pipeline", "0.1")
    include=["aliases", "url-rels", "annotation", "artist-rels"]
    mb_artist = ngs.get_artist_by_id(artist_id, includes=include)['artist']
    mb_artist['item_code'] = mb_artist['id']
    title = mb_artist['name']
    if "disambiguation" in mb_artist:
        title = title + " (" + mb_artist["disambiguation"] + ")"
    mb_artist['title'] = title
    log_text = "artist\t" + str(mb_artist["item_code"]) + "\t" + str(title) + "\r\n"
    mb_artist["log_text"] = log_text
    return mb_artist

#####
# == Process Artist
# Pulls out the artist metadata that we are interested in from the raw MusicBrainz artist meta
#####
def process_artist(mb_artist):
    artist_info = {}
    artist_info['item_code'] = mb_artist['id']
    title = mb_artist['name']
    artist_info['disambiguation'] = ''
    if 'disambiguation' in mb_artist:
        title = title + " (" + mb_artist['disambiguation'] + ") "
        artist_info['disambiguation'] = mb_artist['disambiguation']
    artist_info['title'] = title
    log_text = "artist\t" + str(mb_artist["item_code"]) + "\t" + str(title) + "\r\n"
    artist_info["log_text"] = log_text
    artist_info['name'] = mb_artist['name']
    artist_info['sort_name'] = mb_artist['sort-name']
    artist_info['artist_id'] = mb_artist['id']
    
    artist_info['alias_list'] = []
    if 'alias-list' in mb_artist:
        for alias in mb_artist['alias-list']:
            if 'alias' in alias:
                artist_info['alias_list'].append(mb_artist['alias'])
    
    artist_info['annotation'] = ''
    if 'annotation' in mb_artist:
        if 'annotation' in mb_artist['annotation']:
            artist_info['annotation'] = mb_info[annotation][text]

    artist_info['type'] = ''
    if 'type' in mb_artist:
        artist_info['type'] = mb_artist['type']
    
    artist_info['begin_area_name'] = ''
    artist_info['begin_area_mbid'] = ''
    if 'begin-area' in mb_artist:
        artist_info['begin_area_name'] = mb_artist['begin-area']['name']
        artist_info['begin_area_mbid'] = mb_artist['begin-area']['id']
    
    artist_info['begin_date'] = ''
    artist_info['end_date'] = ''
    artist_info['ended'] = ''
    if 'life-span' in mb_artist:
        if 'begin' in mb_artist["life-span"]:
            artist_info['begin_date'] = mb_artist['life-span']['begin']
        if 'end' in mb_artist['life-span']:
            artist_info['end_date'] = mb_artist['life-span']['end']
        if 'ended' in mb_artist['life-span']:
            artist_info['ended'] = 1 if mb_artist['life-span']['ended'].lower() == 'true' else 0
    
    artist_info['area_name'] = ''
    artist_info['area_mbid'] = ''
    if 'country' in mb_artist:
        artist_info['area_name'] = mb_artist['area']['name']
        artist_info['area_mbid'] = mb_artist['area']['id']
    
    artist_info['end_area_name'] = ''
    artist_info['end_area_mbid'] = ''
    if 'end-area' in mb_artist:
        artist_info['end_area_name'] = mb_artist['end-area']['name']
        artist_info['end_area_mbid'] = mb_artist['area']['id']
        
    artist_info['ipi_list'] = []
    if 'ipi-list' in mb_artist:
        artist_info['ipi_list'] = mb_artist['ipi-list']
    
    artist_info['isni_list'] = []
    if 'isni-list' in mb_artist:
        artist_info['isni_list'] = mb_artist['isni-list']
    
    artist_info['url_list'] = []
    if 'url-relation-list' in mb_artist:
        for link in mb_artist['url-relation-list']:
            if 'target' in link:
                artist_info['url_list'].append(link['target'])
    return artist_info

#####
# == Process Release
# Pulls out the release information that we are interested in from the raw MusicBrainz release
#####
def process_release(mb_release, discnum):
    disc_index = discnum - 1
        
    release_info = {}
    release_info["item_code"] = mb_release['id']
    release_info["release_id"] = mb_release['id']
    release_info["disc_num"] = discnum
    release_info["disc_count"] = len(mb_release["medium-list"])
    release_info["release_title"] = mb_release['title']
    rg = mb_release['release-group']
    release_info["release_group_id"] = rg['id']
    release_info["first_release_date"] = rg['first-release-date']
    if 'tag-list' in rg:
        release_info['tags'] = rg['tag-list']
    else:
        release_info['tags'] = []

    if ('title' in mb_release["medium-list"][disc_index]):
        release_info["disc-title"] = mb_release["medium-list"][disc_index]['title']
            
    if ('format' in mb_release['medium-list'][disc_index]):
        release_info['format'] = mb_release["medium-list"][disc_index]['format']
    else:
        release_info['format'] = ""
        
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
        
    log_text = "release\t" + release_info['item_code'] + "\t" + release_info["release_title"] + "\r\n"
    release_info["log_text"] = log_text

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
    track_info["track_num"] = tracknum + 1 # change track numbers back to 1-index
    track_info["track_count"] = len(mb_release["medium-list"][disc_index]["track-list"])
    track_info["release_track_id"] = track["id"]
    track_info["track_id"] = track["recording"]["id"]
    track_info["title"] = track["recording"]["title"]
    if "length" in track["recording"]:
        track_info["length"] = track["recording"]["length"]
    if ("isrc-list" in track["recording"]):
        track_info["isrcs"] = track["recording"]["isrc-list"]
    track_info["artist-credit"] = track["artist-credit"]
    
    return track_info