__author__ = 'cephalopodblue'
import musicbrainzngs as ngs


class MBInfo():
    default_server = ngs.hostname

    def __init__(self, server, useragent=("hidat_audio_pipeline", "0.1")):
        self.server_location = server
        
        if server != default_server:
            ngs.set_hostname(server)
        
        ngs.set_useragent(useragent[0], useragent[1])

    #####
    # == Get Release
    # Retrieves a raw release from MusicBrainz using their API
    #####
    def get_release(self, release_id):
        include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels", "artists"]
        try:
            mb_release = ngs.get_release_by_id(release_id, includes=include)['release']
        except ngs.ResponseError as e:
            # probably a bad request / mbid
            # propagate up
            raise e
        except ngs.NetworkError as e:
            # can't reach the musicbrainz server - if we have a local, try hitting it?
            mb_release = None
            # propagate error up
            raise e
        
        return mb_release
        
    #####
    # == Get artist
    # Retrieves raw artist metadata from MusicBrainz using their API
    #####
    def get_artist(self, artist_id):
        include=["aliases", "url-rels", "annotation", "artist-rels"]
        return mb_artist