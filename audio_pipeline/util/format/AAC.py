from audio_pipeline.util import Tag
from audio_pipeline.util import Exceptions


class BaseTag(Tag.Tag):

    def set(self, value=Tag.CurrentTag):
        if value is not Tag.CurrentTag:
            self.value = value
            
        if self._value:
            values = list()
            # for val in self._value:
                # values.append(val)
                # values.append(val.encode('utf-8'))
            # try:
                # self.mutagen[self.serialization_name] = values
            # except TypeError:
            self.mutagen[self.serialization_name] = self._value
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
                
    @property
    def value(self):
        if self._value is None:
            return self._value
        else:
            return str(self)
        
    @value.setter
    def value(self, val):
        if val is None:
            self._value = None
        elif isinstance(val, list):
            self._value = val
        else:
            self._value = [val]
        
    def __str__(self):
        rep = ""
        if self._value is not None:
            rep = " ".join([str(val) for val in self._value])
            
        return rep
                
        
class FreeformTag(BaseTag):

    def set(self, value=Tag.CurrentTag):
        if value is not Tag.CurrentTag:
            self.value = value
            
        if self._value:
            try:
                self.mutagen[self.serialization_name] = [str(val).encode('utf-8') for val in self._value]
            except TypeError:
                self.mutagen[self.serialization_name] = [str(val) for val in self._value]
            except AttributeError:
                self.mutagen[self.serialization_name] = [str(val) for val in self._value]
                self.mutagen[self.serialization_name] = [val.encode('utf-8') for val in self.mutagen[self.serialization_name]]
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
    
    def extract(self):
        super().extract()
        
        values = list()
        if self._value:
            for val in self._value:
                values.append(str(val, encoding='utf-8'))
            self._value = values
        
        
class NumberTag(Tag.NumberTagMixin, BaseTag):
    
    def __init__(self, *args):
        self._total = None
        super().__init__(*args)
            
    def extract(self):
        super().extract()
        
        if self._value:
            self._value, self._total = self._value[0]

    def set(self, value=Tag.CurrentTag):
        if value is not Tag.CurrentTag:
            self.value = value
        
        if self._value:
            if self._total:
                val = (self._value, self._total)
            else:
                val = (self._value, 0)
            self.mutagen[self.serialization_name] = [val]
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
            
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        if val is None or isinstance(val, int):
            self._value = val
        elif isinstance(val, str) and self._value_match.match(val):
            self._value = int(val.split('/')[0])
            self._total = int(val.split('/')[1])
        elif isinstance(val, str):
            try:
                self._value = int(val)
            except ValueError:
                raise Exceptions.InvalidTagValueError(str(val) + " is not a valid " + self.name)
        else:
            raise Exceptions.InvalidTagValueError(str(val) + " is not a valid " + self.name)

    def __str__(self):
        if self._value:
            return str(self.value)
        else:
            return ""
            
            
class DiscNumberTag(NumberTag):

    def __str__(self):
        if self._value and self._total:
            return str(self._value) + "/" + str(self._total)
        elif self._value:
            return str(self._value)
        else:
            return ""
            
            
class ReleaseDateTag(Tag.ReleaseDateMixin, BaseTag):

    def __init__(self, *args):
        super().__init__(*args)
        self._normalize()


class Format(Tag.MetadataFormat):

    """
    A static class used to extract and save Vorbis-formated metadata tags.
    """
    # release-level serialization names
    _album = "\xa9alb"
    _album_artist = "aART"
    _release_date = "\xa9day"
    _label = "----:com.apple.iTunes:Label"
    _mbid = "----:com.apple.iTunes:MBID"
    _mbid_p = "----:com.apple.iTunes:MusicBrainz Album Id"
    _media_format = "----:com.apple.iTunes:media"
    _country = "----:com.apple.iTunes:MusicBrainz Album Release Country"
    _release_type = "----:com.apple.iTunes:MusicBrainz Album Type"
    
    # track-level serialization names
    _title = "\xa9nam"
    _artist = "\xa9ART"
    _disc_num = "disk"
    _track_num = "trkn"
    _length = "Length"
    _acoustid = "Acoustid Id"

    # custom tag base
    custom_tag_base = "----:com.apple.iTunes:"

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
        tag = FreeformTag(cls._label_name, cls._label, tags)
        return tag

    @classmethod
    def mbid(cls, tags):
        tag = FreeformTag(cls._mbid_name, cls._mbid_p, tags)
        if tag.value is None:
            tag = FreeformTag(cls._mbid_name, cls._mbid, tags)
        return tag

    @classmethod
    def country(cls, tags):
        tag = FreeformTag(cls._country_name, cls._country, tags)
        return tag

    @classmethod
    def media_format(cls, tags):
        tag = FreeformTag(cls._media_format_name, cls._media_format, tags)
        return tag

    @classmethod
    def release_type(cls, tags):
        tag = FreeformTag(cls._type_name, cls._release_type, tags)
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
        tag = DiscNumberTag(cls._disc_num_name, cls._disc_num, tags)
        return tag

    @classmethod
    def track_num(cls, tags):
        tag = NumberTag(cls._track_num_name, cls._track_num, tags)
        return tag

    @classmethod
    def acoustid(cls, tags):
        tag = cls.custom_tag(cls._acoustid, tags)
        return tag

    #########################
    #   custom tags
    #########################

    @classmethod
    def custom_tag(cls, name, tags):
        serialization_name = cls.custom_tag_base + name
        tag = FreeformTag(name, serialization_name, tags)
        return tag
