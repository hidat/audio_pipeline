from .. import util
from . import TestUtil
import unittest
import mutagen



t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?',
           'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)',
           'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004-04-19',
           'source': 'CD (Lossless)', 'discnumber': 1,
           'accurateripdiscid': '012-0011f4ba-00a8233b-8809700c-4', 'batchid': '50024',
           'encoded by': 'dBpoweramp Release 14.4', 'title': 'Confusion',
           'accurateripresult': 'AccurateRip: Accurate (confidence 62)   [37DEB629]', 
           'artist': 'The Zutons', 'tracknumber': 4, 'disctotal': 1,
           'genre': 'Rock', 'mbid': '5560ffa9-3824-44f4-b2bf-a96ae4864187', 'length': '0:07'}

 
picard_tags = {'tracknumber': 6, 'totaltracks': 13, 'encoded by': 'dBpoweramp Release 14.4', 
            'media': 'CD', 'source': 'CD (Lossless)', 'releasestatus': 'official', 
            'script': 'Latn', 'accurateripresult': 'AccurateRip: Not in database   7CF59426',
            'musicbrainz_trackid': '89715e73-cfa8-487f-8aa1-18c3b7d965b9', 'releasecountry': 'GB',
            'mbid': '232775fc-277d-46e5-af86-5e01764abe5a', 
            'musicbrainz_releasetrackid': 'fe85af54-9982-34cc-9e0a-8d4d13a12350', 'disctotal': 1, 
            'artist': 'Rudi Zygadlo', 'discnumber': 1, 'artists': 'Rudi Zygadlo', 
            'albumartistsort': 'Zygadlo, Rudi', 
            'musicbrainz_albumartistid': '48f12b43-153e-42c3-b67c-212372cbfe2b', 
            'releasetype': 'album', 'batchid': '50024', 
            'accurateripdiscid': '013-0014462a-00cb7579-bf0a3e0d-6', 'tracktotal': 13, 
            'catalognumber': 'ZIQ320CD', 'artistsort': 'Zygadlo, Rudi', 
            'encoder': '(FLAC 1.2.1)', 'musicbrainz_releasegroupid': '06d97cd5-75a4-4ec8-afe3-1127b688c6ee',
            'musicbrainz_artistid': '48f12b43-153e-42c3-b67c-212372cbfe2b', 'totaldiscs': 1, 
            'album': 'Tragicomedies', 'originaldate': '2012-09-17', 'label': 'Planet Mu', 
            'date': '2012-09-17', 'title': 'The Domino Quivers', 'albumartist': 'Rudi Zygadlo', 
            'encoder settings': '-compression-level-5', 'originalyear': '2012', 'length': '0:07'}
 
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

    vorbis_t1 = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.flac")
    vorbis_picard = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.flac")
    vorbis_unknown = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.flac")
    
    aac_t1 = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.m4a")
    aac_picard = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.m4a")
    aac_unknown = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.m4a")       
    
    id3_t1 = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.mp3")
    id3_picard = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.mp3")
    id3_unknown = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.mp3")
    
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
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.flac")
        self.tags = t1_tags
        self.format = util.Vorbis.Format
        
        
class TestReadGenericTagsVorbis_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.flac")
        self.tags = picard_tags
        self.format = util.Vorbis.Format
       
       
class TestReadGenericTagsVorbis_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.flac")
        self.tags = unknown_tags
        self.format = util.Vorbis.Format

        
#############
#   ID3 format tests
#############
        
        
class TestReadGenericTagsID3_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.mp3")
        self.tags = t1_tags
        self.format = util.ID3.Format
     
     
class TestReadGenericTagsID3_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.mp3")
        self.tags = picard_tags
        self.format = util.ID3.Format

        
class TestReadGenericTagsID3_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.MP3")
        self.tags = unknown_tags
        self.format = util.ID3.Format

        
#############
#   AAC format tests
#############


class TestReadGenericTagsAAC_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\t1.m4a")
        self.tags = t1_tags
        self.format = util.AAC.Format
        
        
class TestReadGenericTagsAAC_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\picard.m4a")
        self.tags = picard_tags
        self.format = util.AAC.Format
        
        
class TestReadGenericTagsAAC_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File("audio_pipeline\\test\\test_audio_files\\unknown.m4a")
        self.tags = unknown_tags
        self.format = util.AAC.Format
