import mutagen
import collections
import uuid

from .format import Vorbis, AAC, ID3
from . import Exceptions, Tag
from . import Utilities
from audio_pipeline import Constants


class BaseAudioFile:

    audiofile_type = "BaseAudioFile"

    renameable_tags = {"item_code": "ITEMCODE",
                       "barcode": "Barcode",
                       "catalog_num": "Catalog #",
                       "file_under": "File Under",
                       "obscenity": "FCC Rating",
                       "radio_edit": "Radio Edit",
                       "category": "Category"}

    default_release_width = 15
    default_track_width = 25

    vorbis = Vorbis.Format
    id3 = ID3.Format
    aac = AAC.Format

    def __init__(self, file_name, release_tags=None, track_tags=None,
                 tb_release_tags=None, tb_track_tags=None):
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

        for mime_type in self.audio.mime:
            # get the appropriate tag Format for this file type
            if mime_type in Tag.Formats.mime_map:
                t = Tag.Formats.mime_map[mime_type]
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

        self.release_tags = collections.OrderedDict()
        self.tb_release_tags = []

        self.mbid = self.format.mbid(self.audio)
        self.album = self.format.album(self.audio)
        self.album_artist = self.format.album_artist(self.audio)
        self.release_date = self.format.release_date(self.audio)
        self.label = self.format.label(self.audio)
        self.country = self.format.country(self.audio)
        self.release_type = self.format.release_type(self.audio)
        self.media_format = self.format.media_format(self.audio)

        self.item_code = self.format.custom_tag(BaseAudioFile.renameable_tags["item_code"], self.audio)
        self.barcode = self.format.custom_tag(BaseAudioFile.renameable_tags['barcode'], self.audio)
        self.catalog_num = self.format.custom_tag(BaseAudioFile.renameable_tags['catalog_num'], self.audio)

        # a basic filesystem arrangement - should be easily toggled on/off
        self.file_under = self.format.custom_tag(BaseAudioFile.renameable_tags['file_under'], self.audio)
        if not self.file_under.value:
            artist_value = str(self.album_artist)
            if self.album_artist.value is not None:
                starticle = artist_value.split()[0].casefold()
                if starticle in {"a", "an", "the"} and len(artist_value.split()) > 1:
                    artist_value = artist_value[len(starticle):].strip()
                self.file_under.value = artist_value[0:2].upper()
                self.file_under.save()

        # get custom release tag values
        if release_tags:
            self.release_tags = {r_tag: self.format.custom_tag(r_tag, self.audio) for r_tag in release_tags}
        if tb_release_tags:
            for t in tb_release_tags:
                if t not in self.release_tags:
                    self.release_tags[t] = self.format.custom_tag(t, self.audio)
                self.tb_release_tags.append(t)
        #######################
        #   track-level tags
        #######################
        self.track_tags = collections.OrderedDict()
        self.tb_track_tags = []

        self.title = self.format.title(self.audio)
        self.artist = self.format.artist(self.audio)
        self.disc_num = self.format.disc_num(self.audio)
        self.track_num = self.format.track_num(self.audio)
        self.length = self.format.length(self.audio)
        self.acoustid = self.format.acoustid(self.audio)
        self.recording_mbid = self.format.recording_mbid(self.audio)
        self.track_mbid = self.format.track_mbid(self.audio)

        if track_tags:
            self.track_tags = {t_tag: self.format.custom_tag(t_tag, self.audio) for t_tag in track_tags}
        if tb_track_tags:
            for t in tb_track_tags:
                self.tb_track_tags.append(t)
                if t not in self.track_tags:
                    self.track_tags[t] = self.format.custom_tag(t, self.audio)

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

    def track(self):
        tracks = [self.track_num, self.title, self.artist, self.length, self.item_code, self.track_mbid, self.recording_mbid]
        tracks += [v for v in self.track_tags.values()]
        return tracks

    def tb_release(self):
        TBTag = collections.namedtuple('TBTag', ['width', 'row', 'tag'])

        release_tags = [TBTag(25, 0, self.album_artist), TBTag(30, 0, self.album),
                TBTag(20, 0, self.label), TBTag(10, 0, self.disc_num),
                TBTag(self.default_release_width, 0, self.release_date),
                TBTag(30, 0, self.mbid), TBTag(self.default_release_width, 0, self.country),
                TBTag(self.default_release_width, 1, self.release_type),
                TBTag(self.default_release_width, 1, self.media_format),
                TBTag(self.default_release_width, 1, self.barcode),
                TBTag(self.default_release_width, 1, self.catalog_num)]

        for tag in self.tb_release_tags:
            release_tags.append(TBTag(self.default_release_width, 1, self.release_tags[tag]))

        return release_tags

    def tb_track(self):
        TBTag = collections.namedtuple('TBTag', ['width', 'tag'])
        track_tags = [TBTag(5, self.track_num), TBTag(30, self.title), TBTag(25, self.artist),
                      TBTag(10, self.length)]

        for tag in self.tb_track_tags:
            track_tags.append(TBTag(self.default_track_width, self.track_tags[tag]))

        return track_tags

    def release(self):
        release = [self.album_artist, self.album, self.label, self.disc_num, self.release_date, self.mbid,
                   self.country, self.release_type, self.media_format, self.barcode, self.catalog_num]
        release += [v for v in self.release_tags.values()]

        return release

    def has_minimum_metadata(self):
        """
        Checks if this audiofile has the minimum 'required' metadata -
        album name, album artist name, track name, and track artist name
        :return: True if minimum metadata is there, False otherwise
        """
        min_meta = bool(self.album.value and Utilities.know_artist_name(self.album_artist.value) and self.title.value
                    and Utilities.know_artist_name(self.artist.value))
        print("Has minimum metadata: " + str(min_meta))
        return min_meta

    def should_stuff_metadata(self):
        """
        Checks if this audiofile has already been stuffed with metadata.
        :return: True if audiofile has had metadata stuffed, false otherwise
        """
        return self.meta_stuffed.value

    def has_mbid(self):
        """
        Check whether the track has an MBID value, and that value looks like
        an MBID (i.e. is a UUID)
        :return: True if valid MBID value, False otherwise
        """

        if self.mbid.value:
            try:
                id = uuid.UUID(self.mbid.value)
                return True
            except ValueError as e:
                pass
        return False



class AudioFileFactory:

    audiofiles = dict()
    setup = False

    @classmethod
    def get(cls, file_name):
        if file_name in cls.audiofiles:
            return cls.audiofiles[file_name]
        else:
            af = BaseAudioFile(file_name, Constants.custom_release_tags, Constants.custom_track_tags,
                                     Constants.tb_release_tags, Constants.tb_track_tags)
            cls.audiofiles[file_name] = af
            return af
