import mutagen
import copy

from audio_pipeline import Constants
from .format import Vorbis
from .format import AAC
from .format import ID3
from . import Exceptions
from . import Tag


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
        self._album = None
        self._album_artist = None
        self._release_date = None
        self._label = None

        #######################
        #   track-level tags
        #######################

        self._title = None
        self._artist = None
        self._disc_num = None
        self._track_num = None
        self._length = None
        self.custom_tags = {}
        
    #######################
    #   release-level tags
    #######################

    @property
    def mbid(self):
        return self._get_tag_(self._mbid, self.format.mbid)

    @mbid.setter
    def mbid(self, val):
        self._set_tag_(self._mbid, self.format.mbid, val)

    @property
    def album(self):
        return self._get_tag_(self._album, self.format.album)

    @album.setter
    def album(self, val):
        self._set_tag_(self._album, self.format.album, val)

    @property
    def album_artist(self):
        return self._get_tag_(self._album_artist, self.format.album_artist)

    @album_artist.setter
    def album_artist(self, val):
        self._set_tag_(self._album_artist, self.format.album_artist, val)

    @property
    def release_date(self):
        return self._get_tag_(self._release_date, self.format.release_date)

    @release_date.setter
    def release_date(self, val):
        self._set_tag_(self._release_date, self.format.release_date, val)

    @property
    def label(self):
        return self._get_tag_(self._label, self.format.label)

    @label.setter
    def label(self, val):
        self._set_tag_(self._label, self.format.label, val)

    #######################
    #   track-level tags
    #######################
    
    @property
    def title(self):
        return self._get_tag_(self._title, self.format.title)

    @title.setter
    def title(self, val):
        self._set_tag_(self._title, self.format.title, val)

    @property
    def artist(self):
        return self._get_tag_(self._artist, self.format.artist)

    @artist.setter
    def artist(self, val):
        self._set_tag_(self._artist, self.format.artist, val)

    @property
    def disc_num(self):
        return self._get_tag_(self._disc_num, self.format.disc_num)

    @disc_num.setter
    def disc_num(self, val):
        self._set_tag_(self._disc_num, self.format.disc_num, val)

    @property
    def track_num(self):
        return self._get_tag_(self._track_num, self.format.track_num)

    @track_num.setter
    def track_num(self, val):
        self._set_tag_(self._track_num, self.format.track_num, val)

    @property
    def length(self):
        return self._get_tag_(self._length, self.format.length)

    @length.setter
    def length(self, val):
        self._set_tag_(self._length, self.format.length, val)


    ##################
    # Custom Tags
    ##################
    
    @property
    def item_code(self):
        return self._get_custom_tag_(Constants.custom_tags["item_code"])

    @item_code.setter
    def item_code(self, val):
        self._set_custom_tag_(Constants.custom_tags["item_code"], val)
    
    @property
    def obscenity(self):
        return self._get_custom_tag_(Constants.custom_tags["obscenity"])

    @obscenity.setter
    def obscenity(self, val):
        self._set_custom_tag_(Constants.custom_tags["obscenity"], val)

    @property
    def category(self):
        return self._get_custom_tag_(Constants.custom_tags["category"])

    @category.setter
    def category(self, val):
        self._set_custom_tag_(Constants.custom_tags["category"], val)

    def _get_tag_(self, local_tag, format_tag):
        if not local_tag:
            local_tag = format_tag(self.audio)
        return local_tag

    def _set_tag_(self, local_tag, format_tag, val):
        if isinstance(val, type(format_tag)):
            local_tag = copy.deepcopy(val)
        elif local_tag:
            local_tag.value = val
        else:
            local_tag = format_tag({})
            local_tag.value = val

    def _get_custom_tag_(self, local_tag_name):
        if not self.custom_tags.get(local_tag_name):
            self.custom_tags[local_tag_name] = self.format.custom_tag(local_tag_name, self.audio)
        return self.custom_tags[local_tag_name]

    def _set_custom_tag_(self, local_tag_name, val):
        if isinstance(val, type(self.custom_tags[local_tag_name])):
            self.custom_tags[local_tag_name] = copy.deepcopy(val)
        elif self.custom_tags.get(local_tag_name):
            self.custom_tags[local_tag_name].value = val
        else:
            self.custom_tags[local_tag_name] = self.format.custom_tag(local_tag_name, {})
            self.custom_tags[local_tag_name].value = val

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
        return [self.track_num, self.title, self.artist, self.length, self.obscenity, self.category, self.item_code]
    
    def release(self):
        return [self.album_artist, self.album, self.label, self.disc_num, self.release_date, self.mbid]
