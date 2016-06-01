from .. import util
from . import TestUtil
import unittest
import abc
import mutagen

def TestReleaseProcessor(unittest.TestCase):

    def test_release(self):
        

def TestArtistProcessor(unittest.TestCase):


def TestTrackProcessig(unittest.TestCase):

    def test_artist_name(self):
        vorbis_tag_type = self.vorbis.album_artist
        aac_tag_type = self.aac.album_artist
        id3_tag_type = self.id3.album_artist
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)

        
    def test_mbid(self):
        vorbis_tag_type = self.vorbis.mbid
        aac_tag_type = self.aac.mbid
        id3_tag_type = self.id3.mbid
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)

        
    def test_album(self):
        vorbis_tag_type = self.vorbis.album
        aac_tag_type = self.aac.album
        id3_tag_type = self.id3.album
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)


    def test_release_date(self):
        vorbis_tag_type = self.vorbis.release_date
        aac_tag_type = self.aac.release_date
        id3_tag_type = self.id3.release_date
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)

    def test_title(self):
        vorbis_tag_type = self.vorbis.title
        aac_tag_type = self.aac.title
        id3_tag_type = self.id3.title
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)

    def test_artist(self):
        vorbis_tag_type = self.vorbis.artist
        aac_tag_type = self.aac.artist
        id3_tag_type = self.id3.artist
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)
        
    def test_disc_num(self):
        vorbis_tag_type = self.vorbis.disc_num
        aac_tag_type = self.aac.disc_num
        id3_tag_type = self.id3.disc_num
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)
        
    def test_track_num(self):
        vorbis_tag_type = self.vorbis.track_num
        aac_tag_type = self.aac.track_num
        id3_tag_type = self.id3.track_num
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)
        
    def test_length(self):
        vorbis_tag_type = self.vorbis.length
        aac_tag_type = self.aac.length
        id3_tag_type = self.id3.length
        self.check_tag_equality(vorbis_tag_type, aac_tag_type, id3_tag_type)        
        
    def check_tag_equality(self, vorbis_tag_type, aac_tag_type, id3_tag_type):
        vorbis_tag = vorbis_tag_type(self.vorbis_t1)
        aac_tag = aac_tag_type(self.aac_t1)
        id3_tag = id3_tag_type(self.id3_t1)
        
        msg = "Testing equality of t1 " + vorbis_tag.name + ": "
        self.check_equality(vorbis_tag, aac_tag, id3_tag, msg)
        
        vorbis_tag = vorbis_tag_type(self.vorbis_picard)
        aac_tag = aac_tag_type(self.aac_picard)
        id3_tag = id3_tag_type(self.id3_picard)
        
        msg = "Testing equality of picard " + vorbis_tag.name + ": "
        self.check_equality(vorbis_tag, aac_tag, id3_tag, msg)
        
        vorbis_tag = vorbis_tag_type(self.vorbis_unknown)
        aac_tag = aac_tag_type(self.aac_unknown)
        id3_tag = id3_tag_type(self.id3_unknown)
        
        msg = "Testing equality of unknown " + vorbis_tag.name + ": "
        self.check_equality(vorbis_tag, aac_tag, id3_tag, msg)
