import os.path
import json
from ..util import MBInfo


class TestUtilMixin:

    def check_tag(self, tag_builder, correct):
        tag = tag_builder(self.meta)
        
        self.assertIsNot(tag, None)
        
        if correct is not None:
            self.assertIsNot(tag.value, None, msg="correct tag: " + str(correct))
            self.assertIsNot(tag.value, '')
            # check name & check serialization name
            self.assertEqual(tag.value, correct)
        else:
            self.assertIs(tag.value, None)
            self.assertIs(str(tag), '')
            
    def check_af_tag(self, af_tag, real_tag):
        self.assertIsNot(af_tag, None)
        self.assertIsNot(real_tag, None)
        
        self.assertEqual(af_tag, real_tag)
        
        # more in-depth equality checks
        self.assertEqual(af_tag.name, real_tag.name)
        self.assertEqual(af_tag.serialization_name, real_tag.serialization_name)
        self.assertEqual(af_tag._value, real_tag._value)
        
    def check_af_equality(self, af_1, af_2):
        self.assertEqual(af_1.album, af_2.album)
        self.assertEqual(af_1.album_artist, af_2.album_artist)
        self.assertEqual(af_1.album, af_2.album)
        self.assertEqual(af_1.release_date, af_2.release_date)
        self.assertEqual(af_1.label, af_2.label)
        
        self.assertEqual(af_1.title, af_2.title)
        self.assertEqual(af_1.artist, af_2.artist)
        self.assertEqual(af_1.disc_num, af_2.disc_num)
        self.assertEqual(af_1.track_num, af_2.track_num)
        self.assertEqual(af_1.length, af_2.length)
        

    def check_equality(self, vorbis_tag, aac_tag, id3_tag, msg=None):
        if msg is None:
            msg = ""
            
        self.assertIsNot(vorbis_tag, None)
        self.assertIsNot(aac_tag, None)
        self.assertIsNot(id3_tag, None)
        message = msg + "vorbis and aac not equal"
        self.assertEqual(vorbis_tag, aac_tag, msg=message)
        message = msg + "aac and id3 not equal"
        self.assertEqual(aac_tag, id3_tag, msg=message)
        message = msg + "id3 and vorbis not equal"
        self.assertEqual(id3_tag, vorbis_tag, msg=message)

        
    def check_not_equal(self, vorbis_tag, aac_tag, id3_tag, msg=None):
        if msg is None:
            msg = ""
            
        self.assertIsNot(vorbis_tag, None)
        self.assertIsNot(aac_tag, None)
        self.assertIsNot(id3_tag, None)
        message = msg + "vorbis and aac not equal"
        self.assertNotEqual(vorbis_tag, aac_tag, msg=message)
        message = msg + "aac and id3 not equal"
        self.assertNotEqual(aac_tag, id3_tag, msg=message)
        message = msg + "id3 and vorbis not equal"
        self.assertNotEqual(id3_tag, vorbis_tag, msg=message)
        
        
class TestMBinfo(MBInfo.MBInfo):

    # an 'mbinfo' class to use for testing without constantly hitting musicbrainz
    
    def __init__(self, info_directory, server=None, useragent=("hidat_audio_pipeline", "0.1")):
        """
        An 'mbinfo' class to use when testing, without hitting musicbrainz a ton
        :param info_directory: Directory containing artist & release mbinfo json files
        """
        super().__init__(server, useragent)
        
        self.artist_dir = os.path.join(info_directory, "artists.json")
        self.release_dir = os.path.join(info_directory, "releases.json")
        
        self.artists = {}
        self.releases = {}
        
        if not os.path.exists(info_directory):
            os.mkdir(info_directory)
        else:
            if os.path.exists(self.artist_dir):
                # load in artists
                with open(self.artist_dir, "r") as f:
                    for line in f:
                        if not (line.isspace() or line == ""):
                            artist = json.loads(line)
                            self.artists[artist['id']] = artist
            if os.path.exists(self.release_dir):
                # load in releases
                with open(self.release_dir, "r") as f:
                    for line in f:
                        if not (line.isspace() or line == ""):
                            release = json.loads(line)
                            self.releases[release['id']] = release
                
    def get_release(self, release_id):
        if release_id in self.releases:
            return self.releases[release_id]
        else:
            release = super().get_release(release_id)
            self.releases[release_id] = release
            r = json.dumps(release) + "\r\n"
            with open(self.release_dir, "a+") as f:
                f.write(r)
            return release
                
    def get_artist(self, artist_id):
        if artist_id in self.artists:
            return self.artists[artist_id]
        else:
            artist = super().get_artist(artist_id)
            self.artists[artist_id] = artist
            a = json.dumps(artist) + "\r\n"
            with open(self.artist_dir, "a+") as f:
                f.write(a)
            return artist

