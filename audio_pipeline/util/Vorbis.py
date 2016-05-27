from . import Tag
import re


class BaseTag(Tag.Tag):

    def extract(self):
        super().extract()
        
        if self._value is not None:
            self._value = self._value[0]

    def set(self, value=Tag.CurrentTag):
        if value is not CurrentTag:
            self.value = value
            
        if self._value:
            self.mutagen[self.serialization_name] = [self._value]
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
                
                
class NumberTag(Tag.NumberTagMixin, BaseTag):

    def __init__(self, total_tag, *args):
        self._total = None
        self.serialization_total = total_tag
        super().__init__(*args)        
        
    def extract(self):
        # get the number
        super().extract()
        
        if self._value:
            self._value = int(self._value)
        
        # get the total
        if self.serialization_total in self.mutagen:
            self._total = int(self.mutagen[self.serialization_total][0])

    @property
    def value(self):
        if self._value:
            return self._value

    @value.setter
    def value(self, val):
        if val is None:
            self._value = None
        elif isinstance(val, int):
            self._value = val
        elif isinstance(val, str) and self._value_match.match(val):
            # valid-looking num/total string
            self._value = int(val.split('/')[0])
        else:
            raise Tag.InvalidTagValueError(str(val) + " is not a valid " + self.name)
            

class DiscNumberTag(NumberTag):

    def __str__(self):
        if self._value and self._total:
            val = str(self._value) + "/" + str(self._total)
        elif self._value:
            val = str(self._value)
        else:
            val = ""
            
        return val
        
        
class ReleaseDateTag(Tag.ReleaseDateMixin, BaseTag):
    def __init__(self, *args):
        super().__init__(*args)
        
        
class Format(Tag.MetadataFormat):

    """
    A static class used to extract and save Vorbis-formated metadata tags.
    """
    # release-level serialization names
    _album = "album"
    _album_artist = "albumartist"
    _release_date = "date"
    _label = "label"
    _mbid = "mbid"
    _mbid_p = "musicbrainz_albumid"
    
    # track-level serialization names
    _title = "title"
    _artist = "artist"
    _disc_total = "disctotal"
    _disc_total_picard = "totaldiscs"
    _disc_num = "discnumber"
    _track_total = "tracktotal"
    _track_total_picard = "totaltracks"
    _track_num = "tracknumber"
    _length = "Length"
    
    ################
    #   release-level tags
    ################

    @classmethod
    def album(cls, tags):
        tag = BaseTag(cls._album_name, cls._album, tags)
        return tag

    @classmethod
    def album_artist(cls, tags):
        tag = BaseTag(cls._album_artist_name, cls._album_artist, tags)
        return tag

    @classmethod
    def release_date(cls, tags):
        tag = ReleaseDateTag(cls._release_date_name, cls._release_date, tags)
        return tag

    @classmethod
    def label(cls, tags):
        tag = BaseTag(cls._label_name, cls._label, tags)
        return tag

    @classmethod
    def mbid(cls, tags):
        tag = BaseTag(cls._mbid_name, cls._mbid_p, tags)
        if tag.value is None:
            tag = BaseTag(cls._mbid_name, cls._mbid, tags)
        return tag

    ######################
    #   track-level tags
    ######################

    @classmethod
    def title(cls, tags):
        tag = BaseTag(cls._title_name, cls._title, tags)
        return tag

    @classmethod
    def artist(cls, tags):
        tag = BaseTag(cls._artist_name, cls._artist, tags)
        return tag

    @classmethod
    def disc_num(cls, tags):
        tag = DiscNumberTag(cls._disc_total_picard, cls._disc_num_name, cls._disc_num, tags)
        if tag.total is None:
            tag = DiscNumberTag(cls._disc_total, cls._disc_num_name, cls._disc_num, tags)
        return tag
           
    @classmethod
    def track_num(cls, tags):
        tag = NumberTag(cls._track_total_picard, cls._track_num_name, cls._track_num, tags)
        if tag.total is None:
            tag = NumberTag(cls._track_total, cls._track_num_name, cls._track_num, tags)
        return tag
        
    #########################
    #   custom tags
    #########################

    @classmethod
    def custom_tag(cls, name, tags):
        serialization_name = re.sub("\s", "_", name)
        tag = BaseTag(name, serialization_name, tags)
        return tag
