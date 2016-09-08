__author__ = 'cephalopodblue'
import musicbrainzngs as ngs
from . import Util
import time

RETRY = 5

class MBInfo:
    default_server = ngs.hostname

    def __init__(self, server=None, backup_server=None, useragent=("hidat_audio_pipeline", "0.1")):
        if server is not None and server != self.default_server:
            ngs.set_hostname(server)
            
        self.backup_server = backup_server
        
        ngs.set_useragent(useragent[0], useragent[1])

    @classmethod
    def set_mbhost(cls, server=None):
        cls.default_server = server

    @classmethod
    def set_backup(cls, server=None):
        cls.backup_server = server

    def __do_mb_request(self, request, *args, **kwargs):
        """
        Perform the actual MB request
        :param request: musicbrainzngs method call to perform
        :return:
        """
        mb_meta = None
        for i in range(RETRY):
            try:
                mb_meta = request(*args, **kwargs)
                break
            except ngs.ResponseError as e:
                raise e
            except ngs.NetworkError:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                time.sleep(.2)
                try:
                    mb_meta = request(*args, **kwargs)
                except ngs.NetworkError as e:
                    # if we stil can't reach it, try the backup server (if there is one)
                    if self.backup_server:
                        try:
                            ngs.set_hostname(self.backup_server)
                            mb_meta = request(*args, **kwargs)
                        except ngs.NetworkError as e:
                            # propagate error up
                            time.sleep(.2)
                    else:
                        time.sleep(.2)
        if not mb_meta:
            try:
                mb_meta = request(*args, **kwargs)
            except ngs.ResponseError as e:
                raise e
            except ngs.NetworkError as e:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                raise e

        return mb_meta

    def get_group_releases(self, release_group_id):
        include = ["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels"]
        if Util.is_mbid(release_group_id):
            mb_meta = self.__do_mb_request(ngs.browse_releases, release_group=release_group_id, includes=include)

            if mb_meta:
                return mb_meta['release-list']

    #####
    # == Get Release
    # Retrieves a raw release from MusicBrainz using their API
    #####
    def get_release(self, release_id):
        include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels", "artists"]
        mb_meta = None
        if Util.is_mbid(release_id):
            mb_meta = self.__do_mb_request(ngs.get_release_by_id, release_id, includes=include)

            if mb_meta:
                return mb_meta['release']

    #####
    # == Get artist
    # Retrieves raw artist metadata from MusicBrainz using their API
    #####
    def get_artist(self, artist_id):
        include=["aliases", "url-rels", "annotation", "artist-rels"]
        if Util.is_mbid(artist_id):
            mb_meta = self.__do_mb_request(ngs.get_artist_by_id, artist_id, includes=include)

            if mb_meta:
                return mb_meta['artist']