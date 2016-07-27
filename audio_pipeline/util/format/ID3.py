from audio_pipeline.util import Tag
import mutagen
import mutagen.id3
from audio_pipeline.util import Exceptions


class BaseTag(Tag.Tag):
    _frame_type = mutagen.id3.TXXX
    _frame_encoding = 3

    def __init__(self, *args):
        super().__init__(*args)

    @property
    def value(self):
        if self._value:
            val = str(self._value.text[0])
            return val

    @value.setter
    def value(self, val):
        if val:
            if self._value is None:
                self._value = self._frame_type(self._frame_encoding, val)

            #self._value.text = [val]
        else:
            self._value = None

    def __str__(self):
        if self._value:
            val = str(self.value)
        else:
            val = ""
        return val


class NumberTag(Tag.NumberTagMixin, BaseTag):

    def __init__(self, *args):
        super().__init__(*args)
        self._number = None
        self._total = None
        if self._value:
            values = self._value.text[0].split('/')
            self._number = int(values[0])
            self._total = None
            if len(values) > 1:
                self._total = int(values[1])

    @property
    def value(self):
        if self._number:
            return self._number

    @value.setter
    def value(self, val):
        if val is None:
            self._value = None
        else:
            if isinstance(val, int):
                self._number = val
                if self.total is not None:
                    val = str(val) + "/" + str(self.total)
                else:
                    val = str(val)
            elif isinstance(val, str) and self._value_match.match(val):
                # valid-looking num/total string
                self._number = int(val.split('/')[0])
                self._total = int(val.split('/')[1])
            elif isinstance(val, str):
                try:
                    self._number = int(val)
                except ValueError:
                    raise Exceptions.InvalidTagValueError(str(val) + " is not a valid " + self.name)
            else:
                raise Exceptions.InvalidTagValueError(str(val) + " is not a valid " + self.name)

            if self._value is None:
                self._value = self._frame_type(self._frame_encoding, val)

            self._value.text = [val]

    def __str__(self):
        if self._number:
            val = str(self._number)
        else:
            val = ""
        return val


class CustomTag(BaseTag):
    _frame_type = mutagen.id3.TXXX

    def __init__(self, *args):
        super().__init__(*args)
        self.desc = self.serialization_name[5:]

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, val):
        if val:
            if self._value is None:
                self._value = self._frame_type(self._frame_encoding, self.desc, val)
        else:
            self._value = None

##############
#   release-level id3 tags
##############


class AlbumTag(BaseTag):
    _frame_type = mutagen.id3.TALB


class AlbumArtistTag(BaseTag):
    _frame_type = mutagen.id3.TPE2


class ReleaseDateTag(Tag.ReleaseDateMixin, BaseTag):
    _frame_type = mutagen.id3.TDRC
    
    def __init__(self, *args):
        super().__init__(*args)
        self._normalize()

    @property
    def value(self):
        return super().value
        
    @value.setter
    def value(self, val):
        if val:
            if self._value is None:
                self._value = self._frame_type(self._frame_encoding, val)

            self._value.text[0].text = val
        else:
            self._value = None
    

class LabelTag(BaseTag):
    _frame_type = mutagen.id3.TPUB


class TitleTag(BaseTag):
    _frame_type = mutagen.id3.TIT2


class ArtistTag(BaseTag):
    _frame_type = mutagen.id3.TPE1


class FormatTag(BaseTag):
    _frame_type = mutagen.id3.TMED


class DiscNumberTag(NumberTag):
    _frame_type = mutagen.id3.TPOS

    def __str__(self):
        if self._value:
            val = str(self._value.text[0])
        else:
            val = ""
        return val


class TrackNumberTag(NumberTag):
    _frame_type = mutagen.id3.TRCK


class LengthTag(BaseTag):
    _frame_type = mutagen.id3.TLEN


class Format(Tag.MetadataFormat):

    # release-level serialization names
    _album = "TALB"
    _album_artist = "TPE2"
    _release_date = "TDRC"
    _label = "TPUB"
    _mbid = "TXXX:MBID"
    _mbid_p = "TXXX:MusicBrainz Album Id"
    _release_type = "TXXX:MusicBrainz Album Type"
    _country = "TXXX:MusicBrainz Album Release Country"
    _media_format = "TMED"

    # track-level serialization names
    _title = "TIT2"
    _artist = "TPE1"
    _disc_num = "TPOS"
    _track_num = "TRCK"
    _length = "TLEN"
    _acoustid = "TXXX:Acoustid Id"

    ################
    #   release-level tags
    ################

    @classmethod
    def album(cls, tags):
        tag = AlbumTag(cls._album_name, cls._album, tags)
        return tag

    @classmethod
    def album_artist(cls, tags):
        tag = AlbumArtistTag(cls._album_artist_name, cls._album_artist, tags)
        return tag

    @classmethod
    def release_date(cls, tags):
        tag = ReleaseDateTag(cls._release_date_name, cls._release_date, tags)
        return tag

    @classmethod
    def label(cls, tags):
        tag = LabelTag(cls._label_name, cls._label, tags)
        return tag

    @classmethod
    def mbid(cls, tags):
        tag = CustomTag(cls._mbid_name, cls._mbid_p, tags)
        if tag.value is None:
            tag = CustomTag(cls._mbid_name, cls._mbid, tags)
        return tag

    @classmethod
    def release_type(cls, tags):
        tag = CustomTag(cls._type_name, cls._release_type, tags)
        # if not tag.value:
        #     tag = cls.custom_tag(cls._type_name, tags)
        return tag

    @classmethod
    def country(cls, tags):
        tag = CustomTag(cls._country_name, cls._country, tags)
        # if not tag.value:
        #     tag = cls.custom_tag(cls._country_name, tags)
        return tag

    @classmethod
    def media_format(cls, tags):
        tag = FormatTag(cls._media_format_name, cls._media_format, tags)
        return tag

    ######################
    #   track-level tags
    ######################

    @classmethod
    def title(cls, tags):
        tag = TitleTag(cls._title_name, cls._title, tags)
        return tag

    @classmethod
    def artist(cls, tags):
        tag = ArtistTag(cls._artist_name, cls._artist, tags)
        return tag

    @classmethod
    def disc_num(cls, tags):
        tag = DiscNumberTag(cls._disc_num_name, cls._disc_num, tags)
        return tag

    @classmethod
    def track_num(cls, tags):
        tag = TrackNumberTag(cls._track_num_name, cls._track_num, tags)
        return tag

    @classmethod
    def acoustid(cls, tags):
        tag = CustomTag(cls._acoustid_name, cls._acoustid, tags)
        return tag

    #########################
    #   custom tags
    #########################

    @classmethod
    def custom_tag(cls, name, tags):
        serialization_name = "TXXX:" + str(name)
        tag = CustomTag(name, serialization_name, tags)
        return tag
