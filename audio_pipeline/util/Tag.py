import abc
import re
import copy
from . import Util
from audio_pipeline import Constants
import datetime


class BaseFormats(object):
    formats = []    # list of supported metadata formats
    mime_formats = []   # list of supported formats mime types
    mime_map = {} # mapping of mime types -> supported formats


class Formats(BaseFormats):
    aac = "aac"
    id3 = "id3"
    vorbis = "vorbis"
    
    mime_mp4 = 'audio/mp4'
    mime_m4a = 'audio/mpeg4'
    mime_aac = 'audio/aac'

    mime_mp3 = 'audio/mp3'
    mime_mpg = 'audio/mpg'
    mime_mpeg = 'audio/mpeg'

    mime_flac = 'audio/x-flac'

    formats = [aac, id3, vorbis]
    mime_formats = [mime_mp4, mime_m4a, mime_aac, mime_mp3, mime_mpg,
                    mime_mpeg, mime_flac]
    mime_map = {mime_mp4: aac, mime_m4a : aac, mime_aac: aac,
                mime_mp3: id3, mime_mpg: id3, mime_mpeg: id3,
                mime_flac: vorbis}

                

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
    _country_name = "Country"
    _type_name = "Release Type"
    _media_format_name = "Format"

    # track-level tags
    _title_name = "Title"
    _artist_name = "Artist"
    _disc_num_name = "Disc Num"
    _track_num_name = "Track Num"
    _length_name = "Length"
    _acoustid_name = "Acoustid ID"
    _recording_mbid_name = "Recording MBID"
    _track_mbid_name = "Track MBID"

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

    @classmethod
    @abc.abstractmethod
    def release_type(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def country(cls, mutagen): pass

    @classmethod
    @abc.abstractmethod
    def media_format(cls, mutagen): pass

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

    @classmethod
    @abc.abstractmethod
    def acoustid(cls, mutagen):
        pass
    
    @classmethod
    @abc.abstractmethod
    def track_mbid(cls, mutagen):
        pass
    
    @classmethod
    @abc.abstractmethod
    def recording_mbid(cls, mutagen):
        pass
    
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
    
    def save(self, value=CurrentTag):
        self.set(value)
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
            if isinstance(self._value, list):
                return "\n".join(self._value)
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
        if Constants.ignore_case:
            tag_name = {i.casefold(): i for i in self.mutagen.keys()}
            if self.serialization_name.casefold() in tag_name:
                self.serialization_name = tag_name[self.serialization_name.casefold()]
                self._value = copy.deepcopy(self.mutagen[self.serialization_name])
        elif self.serialization_name in self.mutagen:
            self._value = copy.deepcopy(self.mutagen[self.serialization_name])
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
    _value = None
    _year = None
    _month = None
    _day = None
    delimeters = r"\s*?[\/:\-\s]\s*?"
    
    dates = re.compile("(?P<year>\d\d\d\d)(" + delimeters + ")?(?P<month>\d\d)?(" + delimeters + ")?(?P<day>\d\d)?")

    def _normalize(self):
        # normalize the date string
        # also set the year / month / day
        if self._value:
            normalized = re.subn(self.delimeters, "-", str(self), count=3)[0]
            self.value = normalized

            match = self.dates.search(self.value)
            if match:
                self._year = match.group("year")
                self._month = match.group("month")
                self._day = match.group("day")
    
    def __eq__(self, other):
        if isinstance(other, ReleaseDateMixin):
            return (self.year == other.year and self.month == other.month and self.day == other.day)
        elif isinstance(other, str):
            other_date = self.dates.search(other)
            if other_date:
                return self.year == other_date.group(1) and self.month == other_date.group(2) \
                       and self.day == other_date.group(3)
            else:
                return False
        elif isinstance(other, float):
            return self._value < other
        else:
            super().__eq__(other)

    @property
    def date(self):
        if not (self.month and self.year and self.day):
            d = self.dates.search(self.value)
            self.year = d.group(1)
            self.month = d.group(2)
            self.day = d.group(3)
        if self.month and self.year and self.day:
            return datetime.date(self.year, self.month, self.day)
        
    @property
    def year(self):
        if not self._year:
            self._normalize()
        return self._year
    
    @property
    def month(self):
        if not self._month:
            self._normalize()
        return self._month

    @property
    def day(self):
        if not self._day:
            self._normalize()
        return self._day



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

    def set(self, value=CurrentTag):
        pass

    @property
    def value(self):
        if self._value:
            return Util.minutes_seconds(self._value)

    @value.setter
    def value(self, val):
        pass

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