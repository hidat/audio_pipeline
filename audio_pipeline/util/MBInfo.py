__author__ = 'cephalopodblue'
import musicbrainzngs as ngs
from . import Util
import time


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

    def get_group_releases(self, release_group_id):
        include = ["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels"]
        if Util.is_mbid(release_group_id):
            try:
                mb_meta = ngs.browse_releases(release_group=release_group_id, includes=include)
            except ngs.ResponseError as e:
                raise e
            except ngs.NetworkError:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                time.sleep(.1)
                try:
                    mb_meta = ngs.browse_releases(release_group_id, includes=include)
                except ngs.NetworkError as e:
                    # if we stil can't reach it, try the backup server (if there is one)
                    if self.backup_server:
                        try:
                            ngs.set_hostname(self.backup_server)
                            mb_meta = ngs.browse_releases(release_group_id, includes=include)
                        except ngs.NetworkError as e:
                            # propagate error up
                            raise e
                    else:
                        raise e

            return mb_meta['release-list']

    #####
    # == Get Release
    # Retrieves a raw release from MusicBrainz using their API
    #####
    def get_release(self, release_id):
        include=["artist-credits", "recordings", "isrcs", "media", "release-groups", "labels", "artists"]
        if Util.is_mbid(release_id):
            try:
                mb_meta = ngs.get_release_by_id(release_id, includes=include)
            except ngs.ResponseError as e:
                # probably a bad request / mbid
                # propagate up
                raise e
            except ngs.NetworkError as e:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                time.sleep(.1)
                try:
                    mb_meta = ngs.get_release_by_id(release_id, includes=include)
                except ngs.NetworkError as e:
                    # if we stil can't reach it, try the backup server (if there is one)
                    if self.backup_server:
                        try:
                            ngs.set_hostname(self.backup_server)
                            mb_meta = ngs.get_release_by_id(release_id, includes=include)
                        except ngs.NetworkError as e:
                            # propagate error up
                            raise e
                    else:
                        raise e

            return mb_meta['release']

    #####
    # == Get artist
    # Retrieves raw artist metadata from MusicBrainz using their API
    #####
    def get_artist(self, artist_id):
        include=["aliases", "url-rels", "annotation", "artist-rels"]
        if Util.is_mbid(artist_id):
            try:
                mb_meta = ngs.get_artist_by_id(artist_id, includes=include)
            except ngs.ResponseError as e:
                # probably a bad request / mbid
                # propagate up
                raise e
            except ngs.NetworkError as e:
                # can't reach the musicbrainz server - wait 10 seconds and try again
                time.sleep(.1)
                try:
                    mb_meta = ngs.get_artist_by_id(artist_id, includes=include)
                except ngs.NetworkError as e:
                    # if we stil can't reach it, try the backup server (if there is one)
                    if self.backup_server:
                        try:
                            ngs.set_hostname(self.backup_server)
                            mb_meta = ngs.get_artist_by_id(artist_id, includes=include)
                        except ngs.NetworkError as e:
                            # propagate error up
                            raise e
                    else:
                        raise e

            return mb_meta['artist']