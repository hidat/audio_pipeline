from .. import util
from . import TestUtil
import unittest
import abc
import json
import unicodedata
import xml.etree.ElementTree as et
import os
from ..file_walker import Resources
from ..file_walker import Process


release_file = "audio_pipeline/test/test_files/test_mbids/release_mbids.json"
artist_file = "audio_pipeline/test/test_files/test_mbids/artist_mbids.json"

mb_dir = "audio_pipeline/test/test_files/mb_lookups"

release_results = "audio_pipeline/test/results/processed/Releases"
artist_results = "audio_pipeline/test/results/processed/Artists"


class TestReleaseProcessor(unittest.TestCase):

    def test_release(self):
        dbpoweramp = []
        picard = []
        
        mb = TestUtil.TestMBinfo(mb_dir)
        
        processor = Process.Processor(mb)
        
        with open(release_file, "r") as f:
            releases = json.load(f)
            dbpoweramp = releases["dbpoweramp"]
            picard = releases["picard"]
            
        for release in dbpoweramp:
            self.check_release(release, processor, 'dbpoweramp')

        for release in picard:
            self.check_release(release, processor, 'picard')
            
    def check_release(self, mbid, processor, message):
        # load the appropriate release result
        result = None
        r = mbid + ".xml"
        result_file = os.path.join(release_results, r)
        
        with open(result_file, "rb") as f:
            result = et.parse(f).getroot()
            
        if result:
            processed = processor.get_release(mbid)
            release = processed.release
            for child in result[0]:
                key = child.tag
                value = child.text
                if key in release.__dict__:
                    test_value = release.__dict__[key]
                    if isinstance(value, type(test_value)):
                        message = "PROBLEM WITH " + str(key) + "\n" + message + "\nreal value: " \
                                  + value + "\nacquired value: " + test_value
                        self.assertEqual(value, test_value, msg=message)


class TestArtistProcessor(unittest.TestCase):

    def test_release(self):
        mb = TestUtil.TestMBinfo(mb_dir)

        processor = Process.Processor(mb)

        with open(artist_file, "r") as f:
            artists = json.load(f)

        for artist in artists:
            self.check_artist(artist, processor, 'dbpoweramp')

    def check_artist(self, mbid, processor, message):
        # load the appropriate release result
        r = mbid + ".xml"
        result_file = os.path.join(artist_results, r)

        with open(result_file, "rb") as f:
            result = et.parse(f).getroot()

        if result:
            processed = processor.get_artist(mbid)
            artist = processed.artist
            for child in result[0]:
                key = child.tag
                value = child.text
                if key in artist.__dict__:
                    test_value = artist.__dict__[key]
                    if isinstance(value, type(test_value)):
                        message = "PROBLEM WITH " + str(key) + "\n" + message + "\nreal value: " \
                                  + value + "\nacquired value: " + test_value
                        self.assertEqual(value, test_value, msg=message)
                    elif isinstance(value, Resources.NameId):
                        
                        
    def check_name(self, processed, results):
        if 