from .. import util
from . import TestUtil
import unittest
import abc
import json
import xml.etree.ElementTree as et
import os
from ..file_walker import Process


release_file = "audio_pipeline/test/release_mbids.json"
artist_file = "audio_pipeline/test/artist_mbids.json"

result_dir = "audio_pipeline/test/correct_results"


class TestReleaseProcessor(unittest.TestCase):

    def test_release(self):
        dbpoweramp = []
        picard = []
        
        mb = TestUtil.TestMBinfo(None, result_dir)
        
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
        result_file = os.path.join(result_dir, mbid)
        
        with open(result_file, "r") as f:
            result = et.parse(f).getroot()
            
        if result:
            processed = processor.get_release(mbid)
            for child in result[0]:
                key = child.tag
                value = child.text
                assertequal(value, dict(processed)[key])