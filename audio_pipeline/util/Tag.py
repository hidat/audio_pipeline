import abc

class MetadataFormat(abc.ABCMeta):

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
    def album(cls, value): pass
    
    @classmethod
    @abc.abstractmethod
    def album_artist(cls, value): pass

    @classmethod
    @abc.abstractmethod
    def release_date(cls, value): pass

    @classmethod
    @abc.abstractmethod
    def label(cls, value): pass

    ######################
    #   track-level tags
    ######################
    
    @classmethod
    @abc.abstractmethod
    def title(cls, value): pass

    @classmethod
    @abc.abstractmethod
    def artist(cls, value): pass
    
    @classmethod
    @abc.abstractmethod
    def disc_num(cls, value): pass

    @classmethod
    @abc.abstractmethod
    def track_num(cls, value): pass

    @classmethod
    @abc.abstractmethod
    def length(cls, value): pass
    
    ######################
    #   custom tag makers
    ######################
    
    @classmethod
    @abc.abstractmethod
    def custom_int(cls, name, serialization_name, value): pass

    @classmethod
    @abc.abstractmethod
    def custom_string(cls, name, serialization_name, value): pass
    
    
class VorbisMetadata(MetadataFormat):

    """
    A static class used to extract and save Vorbis-formated metadata tags.
    """
    # release-level serialization names
    _album = "album"
    _album_artist = "albumartist"
    _release_date = "date"
    _label = "label"
    
    # track-level serialization names
    _title = "title"
    _artist = "artist"
    _disc_num = "discnumber"
    _track_num = "tracknumber"
    _length = "Length"
    
    
class Tag(abc.ABCMethod):

    def __init__(self, name, serialization_name, mutagen):
        self.name = name
        self.serialization_name = serialization_name
        self.mutagen = mutagen
        self._value = self.extract(self.mutagen)    
    
    def save(self):
        if self._value:
            formatted_value = self.format(self._value)
            self.mutagen[self.serialization_name] = formatted_value
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
                
        self.mutagen.save()
        
    
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
        
    @abc.abstractmethod
    def extract(self, tags):
        if self.serialization_name in tags:
            raw_value = tags[self.serialization_name]
        else:
            raw_value = None
        return raw_value
        
    @classmethod
    def format(cls, value):
        formatted = str(value)
        return formatted
        
class VorbisStringTag(Tag):
    
    def extract(self, tags):
        

        
class Tags:
    def __init__(self, tag):
        self._tag = tag
        
    @property
    def tag(self):
        return self._tag.value