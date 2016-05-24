import abc
import re

class InvalidTagValueError(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str(self):
        if self.message:
            return str("Invalid Tag Value: " + self.message)
        else:
            return "Invalid Tag Value"
            
            
class CurrentTag:
    value = "Use the current tag value"


class MetadataFormat(abc.ABC):

    """
    A static class used to extract and format metadata tags for a specific metadata format.
    
    Extend this class to encode a new format of metadata tags
    """
    
    ##################
    #   'standard' tag names
    ##################
    
    # release-level tags
    _album_name = "Album"
    _album_artist_name = "Album Artist"
    _release_date_name = "Year"
    _label_name = "Label"
    _mbid_name = "MBID"

    # track-level tags
    _title_name = "Title"
    _artist_name = "Artist"
    _disc_num_name = "Disc Num"
    _track_num_name = "Track Num"
    _length_name = "Length"

    ################
    #   release-level tags
    ################
    
    @classmethod
    @abc.abstractmethod
    def album(cls, tags): pass
    
    @classmethod
    @abc.abstractmethod
    def album_artist(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def release_date(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def label(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def mbid(cls, tags): pass

    ######################
    #   track-level tags
    ######################
    
    @classmethod
    @abc.abstractmethod
    def title(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def artist(cls, tags): pass
    
    @classmethod
    @abc.abstractmethod
    def disc_num(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def track_num(cls, tags): pass

    @classmethod
    @abc.abstractmethod
    def length(cls, tags): pass
    
    ######################
    #   custom tag makers
    ######################

    @classmethod
    @abc.abstractmethod
    def custom_tag(cls, name, tags): pass


class Tag(abc.ABC):

    def __init__(self, name, serialization_name, mutagen):
        self._value = None
        self.mutagen = mutagen
        self.name = name
        self.serialization_name = serialization_name
        self.extract()

    def delete(self):
        self._value = None
        if self.serialization_name in self.mutagen:
            self.mutage.pop(self.serialization_name)
        self.mutagen.save()
    
    def save(self):
        self.set()
        self.mutagen.save()
        
    def set(self, value=CurrentTag):
        if value is not CurrentTag:
            self.value = value
            
        if self._value:
            self.mutagen[self.serialization_name] = self._value
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)

    def __str__(self):
        if self._value:
            return str(self._value)
        else:
            return ""

    @property
    def value(self):
        if self._value:
            return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def extract(self):
        if self.serialization_name in self.mutagen:
            self._value = self.mutagen[self.serialization_name]
        else:
            self._value = None


class NumberTagMixin:
    # just some regex to help format / extract values like "1/2"
    _num_match = re.compile("(?P<type>.+)\s*num", flags=re.I)
    _value_match = re.compile("\d+/\d+", flags=re.I)
    
    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, val):
        if isinstance(val, int):
            self._total = val
        else:
            raise Tag.InvalidTagValueError(str(val) + " is not an integer")
