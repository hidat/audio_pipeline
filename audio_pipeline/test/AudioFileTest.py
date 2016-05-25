from .. import util
import unittest
import abc
import mutagen

t1 = "audio_pipeline\\test\\t1.flac"
t2 = "t2.flac"

t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?',
           'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)',
           'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004 04 19', 'date2': '2004',
           'source': 'CD (Lossless)', 'discnumber': 1,
           'accurateripdiscid': '012-0011f4ba-00a8233b-8809700c-4', 'batchid': '50024',
           'encoded by': 'dBpoweramp Release 14.4', 'title': 'Confusion',
           'accurateripresult': 'AccurateRip: Accurate (confidence 62)   [37DEB629]', 
           'artist': 'The Zutons', 'tracknumber': 4, 'disctotal': 1,
           'genre': 'Rock', 'mbid': '5560ffa9-3824-44f4-b2bf-a96ae4864187'}

t2_tags = {'title': 'The Domino Quivers', 'albumartist': 'Rudi Zygadlo', 
           'encoded by': 'dBpoweramp Release 14.4', 
           'accurateripdiscid': '013-0014462a-00cb7579-bf0a3e0d-6', 
           'date': '2012', 'encoder': '(FLAC 1.2.1)', 'tracktotal': 13, 
           'tracknumber': 6, 'disctotal': 1, 'discnumber': 1, 
           'batchid': '50024', 'accurateripresult': 'AccurateRip: Not in database   [7CF59426]', 
           'source': 'CD (Lossless)', 'artist': 'Rudi Zygadlo', 'album': 'Tragicomedies', 
           'encoder settings': '-compression-level-5'}
           
class TestReadGenericTags:
    def test_artist_name(self):
        tag = self.format.album_artist(self.t1_meta)
        self.check_tag(tag, t1_tags["albumartist"])

    def test_mbid(self):
        tag = self.format.mbid(self.t1_meta)
        self.check_tag(tag, t1_tags["mbid"])
        
    def test_album(self):
        tag = self.format.album(self.t1_meta)
        self.check_tag(tag, t1_tags["album"])
        
    def test_release_date(self):
        if self.format is util.ID3.Format:
            self.skipTest("Date has different format for ID3")
            
        tag = self.format.release_date(self.t1_meta)
        self.check_tag(tag, t1_tags["date"])
        
    def test_release_date_2(self):
        if self.format is not util.ID3.Format:
            self.skipTest("Date only has this format in ID3")
            
        tag = self.format.release_date(self.t1_meta)
        self.check_tag(tag, t1_tags["date2"])
        
    def test_title(self):
        tag = self.format.title(self.t1_meta)
        self.check_tag(tag, t1_tags["title"])
        
    def test_artist(self):
        tag = self.format.artist(self.t1_meta)
        self.check_tag(tag, t1_tags["artist"])
        
    def test_disc_num(self):
        tag = self.format.disc_num(self.t1_meta)
        self.check_tag(tag, t1_tags["discnumber"])
        
    def test_track_num(self):
        tag = self.format.track_num(self.t1_meta)
        self.check_tag(tag, t1_tags["tracknumber"])
        
    def test_length(self):
        tag = self.format.length(self.t1_meta)
        
    def check_empty_tag(self, tag):
        self.assertIsNot(tag, None)
        self.assertIs(tag.value, None)
        self.assertIs(str(tag), '')
        # check name & check serialization name
        
    def check_tag(self, tag, tag_value):
        self.assertIsNot(tag, None)
        self.assertIsNot(tag.value, None)
        self.assertIsNot(tag.value, '')
        # check name & check serialization name
        self.assertEqual(tag.value, tag_value)
        
        
class TestReadGenericTagsFlac(TestReadGenericTags, unittest.TestCase):

    def setUp(self):
        self.t1_meta = mutagen.File("audio_pipeline\\test\\t1.flac")
        self.t2_meta = mutagen.File("audio_pipeline\\test\\t2.flac")
        self.format = util.Vorbis.Format
        
        
class TestReadGenericTagsMP3(TestReadGenericTags, unittest.TestCase):

    def setUp(self):
        self.t1_meta = mutagen.File("audio_pipeline\\test\\t1.mp3")
        self.t2_meta = mutagen.File("audio_pipeline\\test\\t2.mp3")
        self.format = util.ID3.Format
        
        
class TestReadGenericTagsAAC(TestReadGenericTags, unittest.TestCase):

    def setUp(self):
        self.t1_meta = mutagen.File("audio_pipeline\\test\\t1.m4a")
        self.t2_meta = mutagen.File("audio_pipeline\\test\\t2.m4a")
        self.format = util.AAC.Format