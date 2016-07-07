__author__ = 'cephalopodblue'
import musicbrainzngs as ngs
from . import Util
import time


class MBInfo():
    default_server = ngs.hostname

    def __init__(self, server=None, backup_server=None, useragent=("hidat_audio_pipeline", "0.1")):
        if server is not None and server != self.default_server:
            ngs.set_hostname(server)
            
        self.backup_server = backup_server
        
        ngs.set_useragent(useragent[0], useragent[1])

    #####
    # == Get Release
    # Retrieves a raw release from MusicBrainz using their API
    #####
    def get_release(self, release_id):
        if Util.is_mbid(release_id):
            include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels", "artists"]
            try:
                mb_release = ngs.get_release_by_id(release_id, includes=include)['release']
            except ngs.ResponseError as e:
                # probably a bad request / mbid
                # propagate up
                raise e
            except ngs.NetworkError as e:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                time.sleep(.01)
                try: 
                    mb_release = ngs.get_release_by_id(release_id, includes=include)['release']
                except ngs.NetworkError as e:
                    # if we still can't reach it, propagate up the error
                    mb_release = None
                    # propagate error up
                    raise e
            
            return mb_release
        
    #####
    # == Get artist
    # Retrieves raw artist metadata from MusicBrainz using their API
    #####
    def get_artist(self, artist_id):
        if Util.is_mbid(artist_id):
            include=["aliases", "url-rels", "annotation", "artist-rels"]
            
            try:
                mb_artist = ngs.get_artist_by_id(artist_id, includes=include)['artist']
                return mb_artist
            except ngs.ResponseError as e:
                # probably a bad request / mbid
                # propagate up
                raise e
            except ngs.NetworkError as e:
                # can't reach the musicbrainz server - if we have a local, try hitting it?
                mb_artist = None
                # propagate error up
                raise e
