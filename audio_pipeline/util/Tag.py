import abc
import re
from . import Util


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
    def album(cls, mutagen): pass
    
    @classmethod
    @abc.abstractmethod
    def album_artist(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def release_date(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def label(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def mbid(cls, mutagen): pass

    ######################
    #   track-level tags
    ######################
    
    @classmethod
    @abc.abstractmethod
    def title(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def artist(cls, mutagen): pass
    
    @classmethod
    @abc.abstractmethod
    def disc_num(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def track_num(cls, mutagen): pass

    @classmethod
    def length(cls, mutagen):
        tag = LengthTag(cls._length_name, cls._length, mutagen)
        return tag
    
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
            self.mutagen.pop(self.serialization_name)
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
            
    def __eq__(self, other):
        return str(self) == str(other)
    
    def __lt__(self, other):
        return str(self) < str(other)

        
class NumberTagMixin(abc.ABC):
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
            
            
    def __eq__(self, other):
        if (isinstance(other, NumberTagMixin)):
            return self.value == other.value and self.total == other.total
        elif (isinstance(other, int)):
            return self.value == other
        else:
            return str(self) == str(other)
    
    def __lt__(self, other):
        if (isinstance(other, NumberTagMixin)):
            return self.value < other.value
        elif (isinstance(other, int)):
            return self.value < other
        else:
            return str(self) < str(other)
            
            
class ReleaseDateMixin:

    # Normalize all dates
    
    # dates are (generally) separated by one of \, /, :, -, " ",
    # and we'll allow any number of spaces before and after delimeter
    year = "year"
    month = "month"
    day = "day"
    delimeters = "\s*((\\\\|/|:|-)|\s)\s*"
    
    dates = re.compile("(?P<" + year + ">\d\d\d\d)(" + delimeters + 
                       "(?P<" + month + ">\d\d))?(" + delimeters + "(?P<" + day + ">\d\d))?")
                       
    def _normalize(self):
        # normalize the date string
        if self._value:
            normalized = re.subn(self.delimeters, "-", str(self), count=3)[0]
            self.value = normalized

    def __eq__(self, other):
        if isinstance(other, ReleaseDateMixin) or isinstance(other, str):
            d1 = self.dates.search(str(self))
            d2 = self.dates.search(str(other))
            
            if d1 and d2:
                if d1.group(self.year) and d2.group(self.year) and d1.group(self.year) != d2.group(self.year):
                    return False
                elif d1.group(self.month) and d2.group(self.month) and d1.group(self.month) != d2.group(self.month):
                    return False
                elif d1.group(self.day) and d2.group(self.day) and d1.group(self.day) != d2.group(self.day):
                    return False
                else:
                    return True
            elif not (d1 and d2):
                return True
            else:
                return False
        else:
            super().__eq__(other)
        
        
class LengthTag(Tag):
    # regex to help format / extract values
    min = "min"
    sec = "sec"
    _value_match = re.compile("(?P<min>\d\d?):(?P<sec>\d\d)")

    def extract(self):
        self._value = round(self.mutagen.info.length)
        
    def __str__(self):
        if self._value:
            return Util.minutes_seconds(self._value)
        else:
            return ""

    @property
    def value(self):
        if self._value:
            return Util.minutes_seconds(self._value)
            
    def __eq__(self, other):
        if (isinstance(other, LengthTag)):
            return self._value == other._value
        elif isinstance(other, float):
            return self._value == other
        elif isinstance(other, str):
            return (self.value == other or str(self._value) == other)
            
    def __lt__(self, other):
        if isinstance(other, LengthTag):
            return self._value < other._value
        elif isinstance(other, float):
            return self._value < other
        elif isinstance(other, str):
            try:
                o = float(other)
                return self._value < o
            except ValueError:
                if self._value_match(other):
                    seconds = Util.seconds(other)
                    return self._value < seconds
        else:
            raise TypeError("Unorderable types " + str(type(self)) + str(type(other)))