import mutagen

from .format import Vorbis
from .format import AAC
from .format import ID3
from . import Exceptions
from . import Tag


class CustomTags:
    item_code = "ITEMCODE"


class BaseAudioFile:

    vorbis = Vorbis.Format
    id3 = ID3.Format
    aac = AAC.Format
    
    def __init__(self, file_name):
        self._format = None
        self.file_name = file_name
        
        try:
            self.audio = mutagen.File(file_name)
            if not self.audio:
                raise Exceptions.UnsupportedFiletypeError(file_name)
        except IOError as e:
            # if there's an error opening the file (probably not an audio file)
            # propagate the resulting exception on up
            raise e
            
        for type in self.audio.mime:
            # get the appropriate tag Format for this file type
            if type in Tag.Formats.mime_map:
                t = Tag.Formats.mime_map[type]
                self.format = t
                break
                
        if not self.format:
            # Can't process this type of audio file; raise UnsupportedFileType error
            raise Exceptions.UnsupportedFiletypeError(file_name)
            
        # get tags
        
        #######################
        #   release-level tags
        #######################
                
        self._mbid = None        
        self.mbid = property(fget=lambda : self._get_tag_(self._mbid, self.format.mbid),
                             fset=lambda x: self._set_tag_(self._mbid, self.format.mbid, x),
                             doc="MusicBrainz ID of this track's associated release")
                             
        self._album = None        
        self.album = property(fget=lambda : self._get_tag_(self._album, self.format.album),
                             fset=lambda x: self._set_tag_(self._album, self.format.album, x),
                             doc="Album name of the release this track is on.")
                             
        self._album_artist = None        
        self.album_artist = property(fget=lambda : self._get_tag_(self._album_artist, self.format.album_artist),
                             fset=lambda x: self._set_tag_(self._album_artist, self.format.album_artist, x),
                             doc="Album-level artist of the release this track is on.")
                             
        self._release_date = None        
        self.release_date = property(fget=lambda : self._get_tag_(self._release_date, self.format.release_date),
                             fset=lambda x: self._set_tag_(self._release_date, self.format.release_date, x),
                             doc="Release date of the release this track is on.")
        self._label = None        
        self.label = property(fget=lambda : self._get_tag_(self._label, self.format.label),
                             fset=lambda x: self._set_tag_(self._label, self.format.label, x),
                             doc="Label the release this track is on was released under.")

        #######################
        #   track-level tags
        #######################

        self._title = None
        self.title = property(fget=lambda : self._get_tag_(self._title, self.format.title),
                             fset=lambda x: self._set_tag_(self._title, self.format.title, x),
                             doc="Title of this track.")

        self._artist = None
        self.artist = property(fget=lambda : self._get_tag_(self._artist, self.format.artist),
                             fset=lambda x: self._set_tag_(self._artist, self.format.artist, x),
                             doc="Track-level artist.")
                             
        self._disc_num = None
        self.disc_num = property(fget=lambda : self._get_tag_(self._disc_num, self.format.disc_num),
                             fset=lambda x: self._set_tag_(self._disc_num, self.format.disc_num, x),
                             doc="Disc number of the disc this track is on.")
                             
        self._track_num = None
        self.track_num = property(fget=lambda : self._get_tag_(self._track_num, self.format.track_num),
                             fset=lambda x: self._set_tag_(self._track_num, self.format.track_num, x),
                             doc="Track number of this track.")
                             
        self._length = None
        self.length = property(fget=lambda : self._get_tag_(self._length, self.format.length),
                             fset=lambda x: self._set_tag_(self._length, self.format.length, x),
                             doc="Length of this track.")
                             
        self._item_code = None
        self.item_code = property(fget=lambda : self._get_tag_(self._item_code, self.format.item_code),
                             fset=lambda x: self._set_tag_(self._item_code, self.format.item_code, x),
                             doc="Item code of this track.")
                             
        

    def _get_tag_(self, local_tag, format_tag):
        if not local_tag:
            local_tag = format_tag(self.audio)
        return local_tag
        
    def _set_tag_(self, local_tag, format_tag, val):
        if (isinstance(val, type(format_tag))):
            local_tag = copy.deepcopy(val)
        elif self._mbid:
            local_tag.value = val
        else:
            local_tag = format_tag({})
            local_tag.value = val
        
    @property
    def format(self):
        return self._format
        
    @format.setter
    def format(self, val):
        if val.casefold() == "aac":
            self._format = self.aac
        elif val.casefold() == "id3":
            self._format = self.id3
        elif val.casefold() == "vorbis":
            self._format = self.vorbis

    def save(self):
        for item in self:
            item.set()
        self.audio.save()
        
    def __iter__(self):
        release = self.release()
        for item in release:
            yield item
            
        track = self.track()
        for item in track:
            yield item
            
    def track(self):
        return [self.track_num, self.title, self.artist, self.length]
    
    def release(self):
        return [self.album_artist, self.album, self.label, self.disc_num, self.release_date, self.mbid, self.item_code]
