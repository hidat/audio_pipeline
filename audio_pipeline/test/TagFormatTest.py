import os
import unittest

import mutagen
import shutil

import audio_pipeline.test.References as ref
from . import TestUtil
from ..util import format

vorbis_files = dict(t1=os.path.join(ref.format_testing_audio, "t1.flac"), 
                    picard=os.path.join(ref.format_testing_audio, "picard.flac"),
                    unknown=os.path.join(ref.format_testing_audio, "unknown.flac"),
                    to_write=os.path.join(ref.write_testing_audio, "unknown.flac"),
                    copy_to=os.path.join(ref.write_testing_audio, "unknown_copy.flac"))

aac_files = dict(t1=os.path.join(ref.format_testing_audio, "t1.m4a"), 
                 picard=os.path.join(ref.format_testing_audio, "picard.m4a"),
                 unknown=os.path.join(ref.format_testing_audio, "unknown.m4a"),
                 to_write=os.path.join(ref.write_testing_audio, "unknown.m4a"),
                 copy_to=os.path.join(ref.write_testing_audio, "unknown_copy.m4a"))
                 
id3_files = dict(t1=os.path.join(ref.format_testing_audio, "t1.mp3"),
                 picard=os.path.join(ref.format_testing_audio, "picard.mp3"), 
                 unknown=os.path.join(ref.format_testing_audio, "unknown.mp3"),
                 to_write=os.path.join(ref.write_testing_audio, "unknown.mp3"),
                 copy_to=os.path.join(ref.write_testing_audio, "unknown_copy.mp3"))

class TestReadGenericTags(TestUtil.TestUtilMixin):
    def test_artist_name(self):
        self.check_tag(self.format.album_artist, self.tags.get("albumartist"))

    def test_mbid(self):
        self.check_tag(self.format.mbid, self.tags.get("mbid"))
        
    def test_album(self):
        self.check_tag(self.format.album, self.tags.get("album"))
        
    def test_release_date(self):
        self.check_tag(self.format.release_date, self.tags.get("date"))
        
    def test_title(self):
        self.check_tag(self.format.title, self.tags.get("title"))
        
    def test_artist(self):
        self.check_tag(self.format.artist, self.tags.get("artist"))
        
    def test_disc_num(self):
        self.check_tag(self.format.disc_num, self.tags.get("discnumber"))
        
    def test_track_num(self):
        self.check_tag(self.format.track_num, self.tags.get("tracknumber"))
        
    def test_length(self):
        self.check_tag(self.format.length, self.tags.get("length"))

        
#################
#   test tag equality
#################
  

class TestTagEquality(TestUtil.TestUtilMixin, unittest.TestCase):
    vorbis = format.Vorbis.Format
    id3 = format.ID3.Format
    aac = format.AAC.Format

    vorbis_t1 = mutagen.File(vorbis_files["t1"])
    vorbis_picard = mutagen.File(vorbis_files["picard"])
    vorbis_unknown = mutagen.File(vorbis_files["unknown"])
    
    aac_t1 = mutagen.File(aac_files["t1"])
    aac_picard = mutagen.File(aac_files["picard"])
    aac_unknown = mutagen.File(aac_files["unknown"])
    
    id3_t1 = mutagen.File(id3_files["t1"])
    id3_picard = mutagen.File(id3_files["picard"])
    id3_unknown = mutagen.File(id3_files["unknown"])
    
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
           
           
###################
#   Test writing tags
###################

class TestTagWriteToEmptyFile(TestUtil.TestUtilMixin):
    def test_artist_name(self):
        self.write_test(self.format.album_artist, "albumartist")

    def test_mbid(self):
        self.write_test(self.format.mbid, "mbid")
        
    def test_album(self):
        self.write_test(self.format.album, "album")
        
    def test_release_date(self):
        self.write_test(self.format.release_date, "date")
        
    def test_title(self):
        self.write_test(self.format.title, "title")
        
    def test_artist(self):
        self.write_test(self.format.artist, "artist")
        
    def test_disc_num(self):
        self.write_test(self.format.disc_num, "discnumber")
        
    def test_track_num(self):
        self.write_test(self.format.track_num, "tracknumber")
                
    def write_test(self, tag_builder, tag_name):
        correct_tag = self.tags.get(tag_name)
    
        tag = tag_builder(self.meta)
        self.check_tag(tag_builder, None)
        
        tag.value = correct_tag
        tag.save()
        self.meta = mutagen.File(self.file_name)
        
        self.check_tag(tag_builder, correct_tag)

       
#############
#   Vorbis format tests
#############

class TestReadGenericTagsVorbis_t1(TestReadGenericTags, unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.meta = mutagen.File(vorbis_files["t1"])
        self.tags = ref.t1_tags
        self.format = format.Vorbis.Format
        
        
class TestReadGenericTagsVorbis_picard(TestReadGenericTags, unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.meta = mutagen.File(vorbis_files["picard"])
        self.tags = ref.picard_tags
        self.format = format.Vorbis.Format
       
       
class TestReadGenericTagsVorbis_NOMETA(TestReadGenericTags, unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.meta = mutagen.File(vorbis_files["unknown"])
        self.tags = ref.unknown_tags
        self.format = format.Vorbis.Format
        
class TestWriteVorbisTags_t1(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(vorbis_files["to_write"], vorbis_files["copy_to"])
        
        cls.file_name = vorbis_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.t1_tags
        cls.format = format.Vorbis.Format
        
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)


class TestWriteVorbisTags_picard(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(vorbis_files["to_write"], vorbis_files["copy_to"])
        
        cls.file_name = vorbis_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.picard_tags
        cls.format = format.Vorbis.Format
        
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)

#############
#   ID3 format tests
#############
        
        
class TestReadGenericTagsID3_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(id3_files["t1"])
        self.tags = ref.t1_tags
        self.format = format.ID3.Format
     
     
class TestReadGenericTagsID3_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(id3_files["picard"])
        self.tags = ref.picard_tags
        self.format = format.ID3.Format

        
class TestReadGenericTagsID3_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(id3_files["unknown"])
        self.tags = ref.unknown_tags
        self.format = format.ID3.Format

        
class TestWriteId3Tags_t1(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(id3_files["to_write"], id3_files["copy_to"])
        
        cls.file_name = id3_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.t1_tags
        cls.format = format.ID3.Format

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)
    

class TestWriteId3Tags_picard(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(id3_files["to_write"], id3_files["copy_to"])
        
        cls.file_name = id3_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.picard_tags
        cls.format = format.ID3.Format

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)
        
#############
#   AAC format tests
#############


class TestReadGenericTagsAAC_t1(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(aac_files["t1"])
        self.tags = ref.t1_tags
        self.format = format.AAC.Format
        
        
class TestReadGenericTagsAAC_picard(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(aac_files["picard"])
        self.tags = ref.picard_tags
        self.format = format.AAC.Format
        
        
class TestReadGenericTagsAAC_NOMETA(TestReadGenericTags, unittest.TestCase):
    def setUp(self):
        self.meta = mutagen.File(aac_files["unknown"])
        self.tags = ref.unknown_tags
        self.format = format.AAC.Format

        
class TestWriteAACTags_t1(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(aac_files["to_write"], aac_files["copy_to"])
        
        cls.file_name = aac_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.t1_tags
        cls.format = format.AAC.Format
        
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)

        
class TestWriteAACTags_picard(TestTagWriteToEmptyFile, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        shutil.copy(aac_files["to_write"], aac_files["copy_to"])
        
        cls.file_name = aac_files["copy_to"]
        cls.meta = mutagen.File(cls.file_name)
        cls.tags = ref.picard_tags
        cls.format = format.AAC.Format
        
    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_name)
