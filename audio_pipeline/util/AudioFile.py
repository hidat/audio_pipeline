import mutagen

from .format import Vorbis
from .format import AAC
from .format import ID3
from . import Exceptions
from . import Tag


class CustomTags:
    item_code = "ITEMCODE"
    barcode = "BARCODE"
    catalog_num = "CATALOGNUMBER"


class BaseAudioFile:

    default_release_width = 15
    default_track_width = 25

    vorbis = Vorbis.Format
    id3 = ID3.Format
    aac = AAC.Format
    
    def __init__(self, file_name):
        self.format = None
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
                if t.casefold() == "aac":
                    self.format = self.aac
                elif t.casefold() == "id3":
                    self.format = self.id3
                elif t.casefold() == "vorbis":
                    self.format = self.vorbis
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
        self.country = self.format.country(self.audio)
        self.release_type = self.format.release_type(self.audio)
        self.media_format = self.format.media_format(self.audio)

        #######################
        #   track-level tags
        #######################

        self.title = self.format.title(self.audio)
        self.artist = self.format.artist(self.audio)
        self.disc_num = self.format.disc_num(self.audio)
        self.track_num = self.format.track_num(self.audio)
        self.length = self.format.length(self.audio)
        self.acoustid = self.format.acoustid(self.audio)

        self.item_code = self.format.custom_tag(CustomTags.item_code, self.audio)
        self.barcode = self.format.custom_tag(CustomTags.barcode, self.audio)
        self.catalog_num = self.format.custom_tag(CustomTags.catalog_num, self.audio)
        self.meta_stuffed = self.format.custom_tag("meta_stuffed", self.audio)
        
        self.custom_tags = [self.meta_stuffed]

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
            
        for item in self.custom_tags:
            yield item

    def stuff_release(self, release):

        self.mbid.value = release.id
        self.album.value = release.title
        self.album_artist.value = release.artist
        self.release_date.value = release.date
        if len(release.labels) > 0:
            self.label.value = [label.title for label in release.labels]
            self.catalog_num.value = [label.catalog_num for label in release.labels]
        self.country.value = release.country
        if len(release.barcode) > 0:
            self.barcode.value = release.barcode
        if len(release.release_type) > 0:
            self.release_type.value = release.release_type
        if len(release.format) > 0:
            self.media_format.value = release.format[0]
            
    def track(self):
        return [self.track_num, self.title, self.artist, self.length, self.item_code]

    def tb_release(self):
        return [{'width': 25, 'row': 0, 'tag': self.album_artist}, {'width': 30, 'row': 0, 'tag': self.album},
                {'width': 20, 'row': 0, 'tag': self.label}, {'width': 10, 'row': 0, 'tag': self.disc_num},
                {'width': self.default_release_width, 'row': 0, 'tag': self.release_date},
                {'width': 30, 'row': 0, 'tag': self.mbid}, {'width': self.default_release_width, 'row': 0, 'tag': self.country},
                {'width': self.default_release_width, 'row': 1, 'tag': self.release_type},
                {'width': self.default_release_width, 'row': 1, 'tag': self.media_format},
                {'width': self.default_release_width, 'row': 1, 'tag': self.barcode},
                {'width': self.default_release_width, 'row': 1, 'tag': self.catalog_num}]

    def tb_track(self):
        return [{'width': 5, 'tag': self.track_num}, {'width': 30, 'tag': self.title}, {'width': 25, 'tag': self.artist},
                {'width': 10, 'tag': self.length}]
    
    def release(self):
        return [self.album_artist, self.album, self.label, self.disc_num, self.release_date, self.mbid,
                self.country, self.release_type, self.media_format, self.barcode, self.catalog_num]
