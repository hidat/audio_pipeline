import unittest


class TestUtilMixin:

    def check_tag(self, tag, tag_collection, tag_name):
        self.assertIsNot(tag, None)
        
        if tag_name in tag_collection:
            self.assertIsNot(tag.value, None)
            self.assertIsNot(tag.value, '')
            # check name & check serialization name
            self.assertEqual(tag.value, tag_collection[tag_name])
        else:
            self.assertIs(tag.value, None)
            self.assertIs(str(tag), '')
            self.assertNotIn(tag_name, tag_collection)
            
            
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
