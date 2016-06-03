from .. import util
from . import TestUtil
import unittest
import abc
import json
import unicodedata
import xml.etree.ElementTree as et
import os
from ..file_walker import Process


release_file = "audio_pipeline/test/test_mbids/release_mbids.json"
artist_file = "audio_pipeline/test/test_mbids/artist_mbids.json"

mb_dir = "audio_pipeline/test/mb_lookups"

result_dir = "audio_pipeline/test/correct_results/Releases"


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
            self.check_release(release, processor)
            
    def check_release(self, mbid, processor):
        # load the appropriate release result
        result = None
        r = mbid + ".xml"
        result_file = os.path.join(result_dir, r)
        
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
                        message = "PROBLEM WITH " + str(key) + "\nreal value: " + value + "\nacquired value: " + test_value
                        self.assertEqual(value, test_value, msg=message)