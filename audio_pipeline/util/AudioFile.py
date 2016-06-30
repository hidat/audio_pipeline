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
        
        self.mbid = self.format.mbid(self.audio)
        self.album = self.format.album(self.audio)
        self.album_artist = self.format.album_artist(self.audio)
        self.release_date = self.format.release_date(self.audio)
        self.label = self.format.label(self.audio)
                
        #######################
        #   track-level tags
        #######################

        self.title = self.format.title(self.audio)
        self.artist = self.format.artist(self.audio)
        self.disc_num = self.format.disc_num(self.audio)
        self.track_num = self.format.track_num(self.audio)
        self.length = self.format.length(self.audio)
        
        self.item_code = self.format.custom_tag(CustomTags.item_code, self.audio)

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
