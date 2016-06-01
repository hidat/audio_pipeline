from . import Tag
import mutagen


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
                self._value = self._frame_type(encoding=self._frame_encoding)

            self._value.text = [val]
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
        values = self._value.text[0].split('/')
        self._number = int(values[0])
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
            else:
                raise Tag.InvalidTagValueError(str(val) + " is not a valid " + self.name)

            if self._value is None:
                self._value = self._frame_type(encoding=self._frame_encoding)

            self._value.text = [val]

    def __str__(self):
        if self._number:
            val = str(self._number)
        else:
            val = ""
        return val


class CustomTag(BaseTag):
    _frame_type = mutagen.id3.TXXX

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, val):
        if val:
            if self._value is None:
                self._value = self._frame_type(encoding=self._frame_encoding, desc=self.name)
            self._value.text = [val]
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
    

class LabelTag(BaseTag):
    _frame_type = mutagen.id3.TPUB


class TitleTag(BaseTag):
    _frame_type = mutagen.id3.TIT2


class ArtistTag(BaseTag):
    _frame_type = mutagen.id3.TPE1


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

    # track-level serialization names
    _title = "TIT2"
    _artist = "TPE1"
    _disc_num = "TPOS"
    _track_num = "TRCK"
    _length = "TLEN"

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

    #########################
    #   custom tags
    #########################

    @classmethod
    def custom_tag(cls, name, tags):
        serialization_name = "TXXX:" + str(name)
        tag = CustomTag(name, serialization_name, tags)
        return tag
