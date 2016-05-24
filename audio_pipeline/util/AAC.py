from . import Tags


class BaseTag(Tag.Tag):

    def set(self, value=Tag.CurrentTag):
        if value is not CurrentTag:
            self.value = value
            
        if self._value:
            values = list()
            for val in self._value:
                values.append(val.encode('utf-8'))
            self.mutagen[self.serialization_name] = values
        else:
            if self.serialization_name in self.mutagen:
                self.mutagen.pop(self.serialization_name)
                
    @property
    def value(self):
        if self._value is not None:
            return str(self)
        else:
            return self._value
        
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
            rep = " ".join(self._value)
            
        return rep
        
        
class FreeformTag(BaseTag):
    
    def extract(self):
        super().extract()
        
        values = list()
        if self._value:
            for val in self._value:
                values.append(str(val, encoding='utf-8'))
                
        self._value = values
        
        
class NumberTag(Tag.NumberTagMixin, BaseTag):
    
    def __init__(self):
        self._total = None
        super().__init__()
        if len(self._value) > 1:
            # get total
            self._total = self._value[1]
            
    def extract(self):
        super().extract()
        
        if self._value:
            self._value, self._total = self._value[0]
            
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
    
    # track-level serialization names
    _title = "title"
    _artist = "\xa9ART"
    _track_total = "tracktotal"
    _track_num = "trkn"
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
        tag = BaseTag(cls._release_date_name, cls._release_date, tags)
        return tag

    @classmethod
    def label(cls, tags):
        tag = FreeformTag(cls._label_name, cls._label, tags)
        return tag

    @classmethod
    def mbid(cls, tags):
        mbid_tag = FreeformTag(cls._mbid_name, cls._mbid, tags)
        if mbid_tag.value:
            return mbid_tag
        else:
            mbid_p_tag = FreeformTag(cls._mbid_name, cls._mbid_p, tags)
            return mbid_p_tag


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
        tag = DiscNumberTag(cls._disc_total, cls._disc_num_name, cls._disc_num, tags)
        return tag

    @classmethod
    def track_num(cls, tags):
        tag = NumberTag(cls._track_total, cls._track_num_name, cls._track_num, tags)
        return tag

    @classmethod
    def length(cls, tags):
        tag = BaseTag(cls._length_name, cls._length, tags)
        return tag

    #########################
    #   custom tags
    #########################

    @classmethod
    def custom_tag(cls, name, tags):
        serialization_name = re.sub("\s", "_", name)
        tag = BaseTag(name, serialization_name, tags)
        return tag
