import unittest
import audio_pipeline.util as util

t1 = "t1.flac"
t2 = "t2.flac"

t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?',
           'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)',
           'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004 04 19',
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
           
class TestReadGenericTags(unittest.TestCase):
    def setUp(self):
        # initialize AudioFileFactory
        util.AudioFileFactory.audiofile_type = util.AudioFile.AudioFile
        self.t1_meta = util.AudioFileFactory.get_audiofile(t1)
        self.t2_meta = util.AudioFileFactory.get_audiofile(t2)

    def test_artist_name(self):
        tag = t1_meta.album_artist
        self.check_tag(tag, t1_tags["albumartist"])

    def test_mbid(self):
        tag = t1_meta.mbid
        self.check_tag(tag, t1_tags["mbid"])
        
    def test_album(self):
        tag = t1_meta.album
        self.check_tag(tag, t1_tags["album"])
        
    def test_release_date(self):
        tag = t1_meta.release_date
        self.check_tag(tag, t1_tags["date"])
        
    def test_title(self):
        tag = t1_meta.title
        self.check_tag(tag, t1_tags["title"])
        
    def test_artist(self):
        tag = t1_meta.artist
        self.check_tag(tag, t1_tags["artist"])
        
    def test_disc_num(self):
        tag = t1_meta.disc_num
        self.check_tag(tag, t1_tags["discnumber"])
        
    def test_track_num(self):
        tag = t1_meta.track_num
        self.check_tag(tag, t1_tags["tracknumber"])
        
    def test_length(self):
        tag = t1_meta.length
        
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