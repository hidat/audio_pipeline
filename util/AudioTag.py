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
                      mime_mp3: id3, mime_mpg: id3, mime_mpeg : id3,
                      mime_flac: vorbis}


class TagFormat(object):
    def __init__(self, name):
        """
        Store information about a tag for a specific metadata format

        :param name: Tag name, formatted appropriately
        """
        self.name = name                    # formatted tag name
        
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
        if self.name in tags:
            raw_value = tags[self.name]
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
        
        :param formatter: A TagFormat object to format / extract this value
        :param tags: Tags this value is encoded in
        :param release: Release (True) or Track (False) metadata
        """
        self.tag_format = tag_format
        self.value = self.tag_format.extract(tags)
        self.release = release
        self.name = self.tag_format.name
        
    def format(self):
        val = self.tag_format.format(self.value)
        return val
        
        
##############
#   Vorbis Tags
##############

class TagVorbisString(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = str(tags[self.name][0])
        else:
            val = ''
        return val
       
       
class TagVorbisInt(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.name][0])
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
            val = str(tags[self.name][0])
        else:
            val = ''
        return val

class TagAACInt(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.name][0][0])
        return val
        
        
##############
#   ID3 Tags
##############
        
class TagID3String(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = tags[self.name].text[0]
        else:
            val = ''
        return val

        
class TagID3Int(TagFormat):
    def extract(self, tags):
        val = super().extract(tags)
        if val:
            val = int(tags[self.name].text[0].split('/')[0])
        return val
        
        
class TagID3Text(TagID3String):
    def format(self, tag_value):
        name = re.match('(?<=TXXX:)\w+', self.name)
        if name:
            name = name.group(0)
            frame = mutagen.id3.TXXX(encoding=3, desc=name, text=tag_value)
        else:
            frame = mutagen.id3.TXXX(encoding=3, desc=self.name, text=tag_value)

        return frame


class TagID3AlbumName(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TALB(encoding=3, text=tag_value)
        return frame


class TagID3AlbumArtist(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TPE1(encoding=3, text=tag_value)
        return frame


class TagID3TrackNum(TagID3Int):
    def format(self, tag_value):
        frame = mutagen.id3.TRCK(encoding=3, text=tag_value)
        return frame


class TagID3DiscNum(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TPOS(encoding=3, text=tag_value)
        return frame


class TagID3TrackTitle(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TIT2(encoding=3, text=tag_value)
        return frame


class TagID3TrackArtist(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TPE2(encoding=3, text=tag_value)
        return frame


class TagID3Releasedate(TagID3String):
    def format(self, tag_value):
        frame = mutagen.id3.TDRC(encoding=3, text=tag_value)
        return frame
        
        
############
#   KEXP Metadata
############
class KEXP(object):
    def __init__(self):
        self.primary_genre = None
        self.obscenity = None
        
    def primary_genre(self, tags):
        return self.primary_genre.make_tag(tags, False)
        
    def obscenity(self, tags):
        return self.obscenity.make_tag(tags, False)
        
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
        if cls._mbid.name in tags:
            return mbid.make_tag(tags, True)
        elif cls._mbid_p.name in tags:
            return cls._mbid_p.make_tag(tags, True)
        else:
            return None
            
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
        return cls._disc_num.make_tag(tags, False)
        
    @classmethod
    def track_num(cls, tags):
        return cls._track_num.make_tag(tags, False)
        
    @classmethod
    def title(cls, tags):
        return cls._title.make_tag(tags, False)
        
    @classmethod
    def artist(cls, tags):
        return cls._artist.make_tag(tags, False)
        

class AAC(Format):
    
    _mbid = TagAACString('----:com.apple.iTunes:MBID')
    _mbid_p = TagAACString('----:com.apple.iTunes:MusicBrainz Album Id')
    _album = TagAACString('\xa9alb')
    _album_artist = TagAACString('aART')
    _release_date = TagAACString('\xa9day')

    _disc_num = TagAACInt('disk')
    _track_num = TagAACInt('trkn')
    _title = TagAACString('\xa9nam')
    _artist = TagAACString('\xa9ART')


    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = TagAACString('----:com.apple.iTunes:KEXPPRIMARYGENRE')
            self.kexp.obscenity = TagAACString('KEXPFCCOBSCENITYRATING')
            
        
class ID3(Format):

    _mbid = TagID3Text('TXXX:MBID')
    _mbid_p = TagID3Text('TXXX:MusicBrainz Album Id')
    _album = TagID3AlbumName('TALB')
    _album_artist = TagID3AlbumArtist('TPE1')
    _release_date = TagID3Releasedate('TDRC')

    _disc_num = TagID3DiscNum('TPOS')
    _track_num = TagID3TrackNum('TRCK')
    _title = TagID3TrackTitle('TIT2')
    _artist = TagID3TrackArtist('TPE2')

    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = TagID3Text('TXXX:KEXPPRIMARYGENRE')
            self.kexp.obscenity = TagID3Text('TXXX:KEXPFCCOBSCENITYRATING')

        
class Vorbis(Format):
    _mbid = TagVorbisString('mbid')
    _mbid_p = TagVorbisString('musicbrainz_albumid')
    _album = TagVorbisString('album')
    _album_artist = TagVorbisString('albumartist')
    _release_date = TagVorbisString('date')

    _disc_num = TagVorbisInt('discnumber')
    _track_num = TagVorbisInt('tracknumber')
    _title = TagVorbisString('title')
    _artist = TagVorbisString('artist')

    def __init__(self, kexp=False):
        self.kexp = None
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = TagVorbisString('KEXPPRIMARYGENRE')
            self.kexp.obscenity = TagVorbisString('KEXPFCCOBSCENITYRATING')