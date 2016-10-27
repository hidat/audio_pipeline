import os
import unittest

import mutagen

from . import TestUtil
from .. import util

test_files = "audio_pipeline\\test\\test_files\\audio\\tag_test_files"

class TestAudioFileTags(TestUtil.TestUtilMixin):
    def test_artist_name(self):
        tag = self.format.album_artist(self.meta)
        self.check_af_tag(tag, self.af.album_artist)

    def test_mbid(self):
        tag = self.format.mbid(self.meta)
        self.check_af_tag(tag, self.af.mbid)
        
    def test_album(self):
        tag = self.format.album(self.meta)
        self.check_af_tag(tag, self.af.album)
        
    def test_release_date(self):
        tag = self.format.release_date(self.meta)
        self.check_af_tag(tag, self.af.release_date)
        
    def test_title(self):
        tag = self.format.title(self.meta)
        self.check_af_tag(tag, self.af.title)
        
    def test_artist(self):
        tag = self.format.artist(self.meta)
        self.check_af_tag(tag, self.af.artist)
        
    def test_disc_num(self):
        tag = self.format.disc_num(self.meta)
        self.check_af_tag(tag, self.af.disc_num)
        
    def test_track_num(self):
        tag = self.format.track_num(self.meta)
        self.check_af_tag(tag, self.af.track_num)
        
    def test_length(self):
        tag = self.format.length(self.meta)
        self.check_af_tag(tag, self.af.length)

    def test_custom_release(self):
        for tag_name in self.af.custom_release_tags.keys():
            tag = self.format.custom_tag(tag_name, self.meta)
            self.check_af_tag(tag, self.af.custom_release_tags[tag_name])

    def test_custom_track(self):
        for tag_name in self.af.custom_track_tags.keys():
            tag = self.format.custom_tag(tag_name, self.meta)
            self.check_af_tag(tag, self.af.custom_track_tags[tag_name])
        

class TestAudioFileVorbis_t1(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "t1.flac"))
    format = util.format.Vorbis.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "t1.flac"))
    
    
class TestAudioFileVorbis_picard(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "picard.flac"))
    format = util.format.Vorbis.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "picard.flac"))
    
    
class TestAudioFileVorbis_unknown(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "unknown.flac"))
    format = util.format.Vorbis.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "unknown.flac"))
    
    
class TestAudioFileAAC_t1(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "t1.m4a"))
    format = util.format.AAC.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "t1.m4a"))
    
    
class TestAudioFileAAC_picard(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "picard.m4a"))
    format = util.format.AAC.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "picard.m4a"))
    
    
class TestAudioFileAAC_unknown(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "unknown.m4a"))
    format = util.format.AAC.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "unknown.m4a"))
    
    
class TestAudioFileID3_t1(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "t1.mp3"))
    format = util.format.ID3.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "t1.mp3"))
    
    
class TestAudioFileID3_picard(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "picard.mp3"))
    format = util.format.ID3.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "picard.mp3"))
    
    
class TestAudioFileID3_unknown(TestAudioFileTags, unittest.TestCase):

    meta = mutagen.File(os.path.join(test_files, "unknown.mp3"))
    format = util.format.ID3.Format

    af = util.AudioFile.BaseAudioFile(os.path.join(test_files, "unknown.mp3"))