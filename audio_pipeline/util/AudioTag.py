import mutagen.id3
import re


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


class TagFormat(object):
    def __init__(self, tag_name, name):
        """
        Store information about a tag for a specific metadata format

        :param name: Tag name, formatted appropriately
        """
        self.tag_name = tag_name            # formatted tag name
        self.name = name                    # 'standard' tag name
        
    def format(self, tag_value):
        """
        Format the tag value for this tag.

        :param tag_value: The value of the tag value
        :return: Tag value formatted appropriately
        """
        formatted = str(tag_value)
        return formatted
        
    def extract(self, tags):
        """
        Extract a tag value from a formatted tag value string
        
        :param tags: Metadata tags
        :return: Raw value
        """
        if self.tag_name in tags:
            raw_value = tags[self.tag_name]
        else:
            raw_value = None
        return raw_value
        
    def make_tag(self, tags, release):
        """
        Make a new Tag object encapsulating a certain tag value
        
        :param tags: Mutagen tags
        :param release: True if this tag is release metadata, False otherwise
        :return: new tag object representing the value tags[self.name]
        """
        return Tag(self, tags, release)
        

class Tag(object):
    def __init__(self, tag_format, tags, release):
        """
        Represents a specific tag value
        
        :param tag_format: A TagFormat object to format / extract this value
        :param tags: Tags this value is encoded in
        :param release: Release (True) or Track (False) metadata
        """
        self.formatter = tag_format.format
        self.value = tag_format.extract(tags)
        self.release = release
        self.name = tag_format.name
        self.tag_name = tag_format.tag_name

    def format(self):
        val = self.formatter(self.value)
        return val
        
        
##############
#   Vorbis Tags
##############

class TagVorbisString(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = str(tags[self.tag_name][0])
        else:
            val = ''
        return val
       
       
class TagVorbisInt(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.tag_name][0])
        return val

##############
#   AAC Tags
##############


class TagAACString(TagFormat):
    def format(self, tag_value):
        formatted = tag_value.encode('utf-8')
        return formatted
        
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = str(tags[self.tag_name][0])
        else:
            val = ''
        return val

class TagAACInt(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.tag_name][0][0])
        return val

        
class TagAACFreeform(TagAACString):
    def extract(self, tags):
        if self.tag_name in tags:
            val = str(tags[self.tag_name][0], encoding='UTF-8')
        else:
            val = ''
            
        return val

        
##############
#   ID3 Tags
##############


class TagID3String(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = tags[self.tag_name].text[0]
        else:
            val = ''
        return val

        
class TagID3Int(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.tag_name].text[0].split('/')[0])
        return val
        
        
class TagID3Text(TagID3String):
    def format(self, tag_value):
        val = str(tag_value)
        name = re.search('(?<=TXXX:)\w+', self.tag_name)
        if name:
            name = name.group(0)
            frame = mutagen.id3.TXXX(encoding=3, desc=name, text=val)
        else:
            frame = mutagen.id3.TXXX(encoding=3, desc=self.tag_name, text=val)
        return frame


class TagID3AlbumName(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TALB(encoding=3, text=tag_value)
        return frame


class TagID3AlbumArtist(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TPE2(encoding=3, text=tag_value)
        return frame


class TagID3TrackNum(TagID3Int):
    def format(self, tag_value):
        val = str(tag_value)
        frame = mutagen.id3.TRCK(encoding=3, text=val)
        return frame


class TagID3DiscNum(TagID3String):
    def format(self, tag_value):
        val = str(tag_value)
        frame = mutagen.id3.TPOS(encoding=3, text=val)
        return frame


class TagID3TrackTitle(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TIT2(encoding=3, text=tag_value)
        return frame


class TagID3TrackArtist(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TPE1(encoding=3, text=tag_value)
        return frame


class TagID3Releasedate(TagID3String):
    def format(self, tag_value):
        val = str(tag_value)
        frame = mutagen.id3.TDRC(encoding=3, text=val)
        return frame
        
class TagID3Label(TagID3String):
    def format(self, tag_value):
        val = str(tag_value)
        frame = mutagen.id3.TPUB(encoding=3, text=val)
        return frame
        
        
############
#   KEXP Metadata
############
class KEXP(object):
    def __init__(self):
        self._primary_genre = None
        self._obscenity = None
        
    def primary_genre(self, tags):
        return self._primary_genre.make_tag(tags, False)
        
    def obscenity(self, tags):
        return self._obscenity.make_tag(tags, False)
        
############
#   Format Metadata Tags
############

class Format(object):
    _mbid = None
    _mbid_p = None
    _album = None
    _album_artist = None
    _release_date = None

    _disc_num = None
    _track_num = None
    _title = None
    _artist = None

    def __init__(self, kexp=False):
        self.kexp = None
        
    @classmethod        
    def mbid(cls, tags):
        if cls._mbid.tag_name in tags:
            return cls._mbid.make_tag(tags, True)
        else:
            return cls._mbid_p.make_tag(tags, True)
            
    @classmethod
    def album(cls, tags):
        return cls._album.make_tag(tags, True)
        
    @classmethod
    def album_artist(cls, tags):
        return cls._album_artist.make_tag(tags, True)
        
    @classmethod
    def release_date(cls, tags):
        return cls._release_date.make_tag(tags, True)
        
    @classmethod
    def disc_num(cls, tags):
        return cls._disc_num.make_tag(tags, True)
        
    @classmethod
    def track_num(cls, tags):
        return cls._track_num.make_tag(tags, False)
        
    @classmethod
    def title(cls, tags):
        return cls._title.make_tag(tags, False)
        
    @classmethod
    def artist(cls, tags):
        return cls._artist.make_tag(tags, False)
        
    @classmethod
    def label(cls, tags):
        return cls._label.make_tag(tags, True)
        

class AAC(Format):
    
    _mbid = TagAACFreeform('----:com.apple.iTunes:MBID', 'MBID')
    _mbid_p = TagAACFreeform('----:com.apple.iTunes:MusicBrainz Album Id', 'MBID')
    _album = TagAACString('\xa9alb', 'Album')
    _album_artist = TagAACString('aART', 'Album Artist')
    _release_date = TagAACString('\xa9day', 'Year')
    _label = TagAACFreeform('----:com.apple.iTunes:LABEL', 'Label')

    _disc_num = TagAACInt('disk', 'Disc Num')
    _track_num = TagAACInt('trkn', 'Track Num')
    _title = TagAACString('\xa9nam', 'Title')
    _artist = TagAACString('\xa9ART', 'Artist')

    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp._primary_genre = TagAACFreeform('----:com.apple.iTunes:KEXPPRIMARYGENRE', 'KEXP Primary Genre')
            self.kexp._obscenity = TagAACFreeform('----:com.apple.iTunes:KEXPFCCOBSCENITYRATING', 'KEXPFCCOBSCENITYRATING')
            
        
class ID3(Format):

    _mbid = TagID3Text('TXXX:MBID', 'MBID')
    _mbid_p = TagID3Text('TXXX:MusicBrainz Album Id', 'MBID')
    _album = TagID3AlbumName('TALB', 'Album')
    _album_artist = TagID3AlbumArtist('TPE2', 'Album Artist')
    _release_date = TagID3Releasedate('TDRC', 'Year')
    _label = TagID3Label('TPUB', 'Label')
    
    _disc_num = TagID3DiscNum('TPOS', 'Disc Num')
    _track_num = TagID3TrackNum('TRCK', 'Track Num')
    _title = TagID3TrackTitle('TIT2', 'Title')
    _artist = TagID3TrackArtist('TPE1', 'Artist')

    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp._primary_genre = TagID3Text('TXXX:KEXPPRIMARYGENRE', 'KEXP Primary Genre')
            self.kexp._obscenity = TagID3Text('TXXX:KEXPFCCOBSCENITYRATING', 'KEXPFCCOBSCENITYRATING')

        
class Vorbis(Format):
    _mbid = TagVorbisString('mbid', 'MBID')
    _mbid_p = TagVorbisString('musicbrainz_albumid', 'MBID')
    _album = TagVorbisString('album', 'Album')
    _album_artist = TagVorbisString('albumartist', 'Album Artist')
    _release_date = TagVorbisString('date', 'Year')
    _label = TagVorbisString('label', 'Label')
    
    _disc_num = TagVorbisInt('discnumber', 'Disc Num')
    _track_num = TagVorbisInt('tracknumber', 'Track Num')
    _title = TagVorbisString('title', 'Title')
    _artist = TagVorbisString('artist', 'Artist')

    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp._primary_genre = TagVorbisString('KEXPPRIMARYGENRE', 'KEXP Primary Genre')
            self.kexp._obscenity = TagVorbisString('KEXPFCCOBSCENITYRATING', 'KEXPFCCOBSCENITYRATING')