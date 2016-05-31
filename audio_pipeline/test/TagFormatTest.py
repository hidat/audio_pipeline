from .. import util
from . import TestUtil
import unittest
import mutagen



t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?',
           'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)',
           'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004 04 19',
           'source': 'CD (Lossless)', 'discnumber': 1,
           'accurateripdiscid': '012-0011f4ba-00a8233b-8809700c-4', 'batchid': '50024',
           'encoded by': 'dBpoweramp Release 14.4', 'title': 'Confusion',
           'accurateripresult': 'AccurateRip: Accurate (confidence 62)   [37DEB629]', 
           'artist': 'The Zutons', 'tracknumber': 4, 'disctotal': 1,
           'genre': 'Rock', 'mbid': '5560ffa9-3824-44f4-b2bf-a96ae4864187', 'length': '0:07'}

picard_tags = {'label': 'Lost Highway Records', 'catalognumber': 'B0005872-02',
               'musicbrainz_albumid': 'b22613bf-8082-4d1a-9946-f4a5e9a4a76f', 'producer': 'Ethan Johns',
               'releasestatus': 'official', 'barcode': '602498878484',
               'musicbrainz_artistid': 'c80f38a6-9980-485d-997c-5c1a9cbd0d64', 'media': 'CD', 'disctotal': 1,
               'musicbrainz_albumartistid': 'c80f38a6-9980-485d-997c-5c1a9cbd0d64',
               'musicbrainz_releasetrackid': 'd6a1b004-f4f5-3b8c-8cd8-d8aa7d72fe8f', 'tracknumber': 3, 'discnumber': 1,
               'musicbrainz_releasegroupid': '5fe118c7-ef72-3c22-8706-b8027ef1b53c', 'originaldate': '2005-12-20',
               'artistsort': 'Adams, Ryan', 'artist': 'Ryan Adams', 'script': 'Latn',
               'musicbrainz_trackid': 'e1d709de-a8f5-4197-a9a2-69bd4fa81bb7', 'totaltracks': 9,
               'artists': 'Ryan Adams', 'album': '29', 'title': 'Nightbirds', 'releasetype': 'album', 'totaldiscs': 1,
               'tracktotal': 9, 'date': '2005-12-20', 'mixer': 'Ethan Johns', 'releasecountry': 'US',
               'isrc': 'USUM70506034', 'albumartist': 'Ryan Adams', 'albumartistsort': 'Adams, Ryan',
               'mbid': 'b22613bf-8082-4d1a-9946-f4a5e9a4a76f', 'length': '0:07'}

unknown_tags = {'accurateripresult': 'AccurateRip: Not in database   7A470C62', 
                'source': 'CD (Lossless) >> Perfect (Lossless) m4a', 
                'artist': 'Unknown Artist', 'disctotal': 1, 'tracktotal': 12,
                'accurateripdiscid': '012-0010ae26-009c5221-8e08ec0c-4',
                'encoded by': 'dBpoweramp Release 14.4', 'encoder': '(FLAC 1.2.1)',
                'title': 'Track04', 'tracknumber': 4, 'discnumber': 1, 'length': '0:07'}

class TestReadGenericTags(TestUtil.TestUtilMixin):
    def test_artist_name(self):
        tag = self.format.album_artist(self.meta)
        self.check_tag(tag, self.tags, "albumartist")

    def test_mbid(self):
        tag = self.format.mbid(self.meta)
        self.check_tag(tag, self.tags, "mbid")
        
    def test_album(self):
        tag = self.format.album(self.meta)
        self.check_tag(tag, self.tags, "album")
        
    def test_release_date(self):
        tag = self.format.release_date(self.meta)
        self.check_tag(tag, self.tags, "date")
        
    def test_title(self):
        tag = self.format.title(self.meta)
        self.check_tag(tag, self.tags, "title")
        
    def test_artist(self):
        tag = self.format.artist(self.meta)
        self.check_tag(tag, self.tags, "artist")
        
    def test_disc_num(self):
        tag = self.format.disc_num(self.meta)
        self.check_tag(tag, self.tags, "discnumber")
        
    def test_track_num(self):
        tag = self.format.track_num(self.meta)
        self.check_tag(tag, self.tags, "tracknumber")
        
    def test_length(self):
        tag = self.format.length(self.meta)
        self.check_tag(tag, self.tags, "length")
       
#################
#   test tag equality
#################
  

class TestTagEquality(TestUtil.TestUtilMixin, unittest.TestCase):
    vorbis = util.Vorbis.Format
    id3 = util.ID3.Format
    aac = util.AAC.Format

    vorbis_t1 = mutagen.File("audio_pipeline\\test\\t1.flac")
    vorbis_picard = mutagen.File("audio_pipeline\\test\\picard.flac")
    vorbis_unknown = mutagen.File("audio_pipeline\\test\\unknown.flac")
    
    aac_t1 = mutagen.File("audio_pipeline\\test\\t1.m4a")
    aac_picard = mutagen.File("audio_pipeline\\test\\picard.m4a")
    aac_unknown = mutagen.File("audio_pipeline\\test\\unknown.m4a")       
    
    id3_t1 = mutagen.File("audio_pipeline\\test\\t1.mp3")
    id3_picard = mutagen.File("audio_pipeline\\test\\picard.mp3")
    id3_unknown = mutagen.File("audio_pipeline\\test\\unknown.mp3")
    
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
           
       
#############
#   Vorbis format tests
#############
   
   
class TestReadGenericTagsVorbis_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\t1.flac")
        self.tags = t1_tags
        self.format = util.Vorbis.Format
        
        
class TestReadGenericTagsVorbis_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\picard.flac")
        self.tags = picard_tags
        self.format = util.Vorbis.Format
       
       
class TestReadGenericTagsVorbis_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\unknown.flac")
        self.tags = unknown_tags
        self.format = util.Vorbis.Format

        
#############
#   ID3 format tests
#############
        
        
class TestReadGenericTagsID3_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\t1.mp3")
        self.tags = t1_tags
        self.format = util.ID3.Format
     
     
class TestReadGenericTagsID3_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\picard.mp3")
        self.tags = picard_tags
        self.format = util.ID3.Format

        
class TestReadGenericTagsID3_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\unknown.MP3")
        self.tags = unknown_tags
        self.format = util.ID3.Format

        
#############
#   AAC format tests
#############


class TestReadGenericTagsAAC_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\t1.m4a")
        self.tags = t1_tags
        self.format = util.AAC.Format
        
        
class TestReadGenericTagsAAC_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\picard.m4a")
        self.tags = picard_tags
        self.format = util.AAC.Format
        
        
class TestReadGenericTagsAAC_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\unknown.m4a")
        self.tags = unknown_tags
        self.format = util.AAC.Format
