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
    
#####
# == Get artist
# Retrieves raw artist metadata from MusicBrainz using their API
#####
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
