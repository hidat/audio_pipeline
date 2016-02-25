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


class Tag(object):
    def __init__(self, name):
        """
        Store information about a tag for a specific metadata format

        :param name: Tag name, formatted appropriately
        """
        self.name = name

    def format(self, tag_value):
        """
        Format the tag value for this tag.

        :param tag_value: The value of the tag value
        :return: Tag value formatted appropriately
        """
        formatted = str(tag_value)
        return formatted
        
    @classmethod
    def extract_str(self, raw_value):
        """
        Extract a tag value from a formatted tag value string
        
        :param raw_value: Raw tag value
        :return: Plain utf-8 string tag value
        """
        val = raw_value[0]
        return val
        
    @classmethod
    def extract_int(self, raw_value):
        """
        Extract an integer tag value from a formatted tag value
        
        :param raw_value: Raw tag value
        :return: Integer value of tag
        """
        val = raw_value[0]
        return int(val)

##############
#   AAC Tags
##############
        
class TagAAC(Tag):
    def format(self, tag_value):
        formatted = tag_value.encode('utf-8')
        return formatted
        
    @classmethod
    def extract_str(self, raw_value):
        val = str(raw_value[0])
        return val
        
    @classmethod
    def extract_int(self, raw_value):
        val = int(raw_value[0][0])
        return val
        
        
##############
#   ID3 Tags
##############
        
class TagID3(Tag):
    @classmethod
    def extract_str(self, raw_value):
        val = raw_value.text[0]
        return val
        
    @classmethod
    def extract_int(self, raw_value):
        val = int(raw_value.text[0].split('/')[0])
        return val
        
        
class TagID3Text(TagID3):
    def format(self, tag_value):
        name = re.match('(?<=TXXX:)\w+', self.name)
        if name:
            name = name.group(0)
            frame = mutagen.id3.TXXX(encoding=3, desc=name, text=tag_value)
        else:
            frame = mutagen.id3.TXXX(encoding=3, desc=self.name, text=tag_value)

        return frame


class TagID3AlbumName(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TALB(encoding=3, text=tag_value)
        return frame


class TagID3AlbumArtist(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TPE1(encoding=3, text=tag_value)
        return frame


class TagID3TrackNum(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TRCK(encoding=3, text=tag_value)
        return frame


class TagID3DiscNum(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TPOS(encoding=3, text=tag_value)
        return frame


class TagID3TrackTitle(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TIT2(encoding=3, text=tag_value)
        return frame


class TagID3TrackArtist(TagID3):
    def format(self, tag_value):
        frame = mutagen.id3.TPE2(encoding=3, text=tag_value)
        return frame


class TagID3Releasedate(TagID3):
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


class AAC(object):
    def __init__(self, kexp=False):
        self.kexp = None
    
        self.mbid = TagAAC('----:com.apple.iTunes:MBID')
        self.mbid_p = TagAAC('----:com.apple.iTunes:MusicBrainz Album Id')
        self.album = TagAAC('\xa9alb')
        self.album_artist = TagAAC('\xa9ART')
        self.release_date = TagAAC('aART')

        self.disc_num = TagAAC('disk')
        self.track_num = TagAAC('trkn')
        self.title = TagAAC('\xa9nam')
        self.artist = TagAAC('\xa9ART')
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = TagAAC('----:com.apple.iTunes:KEXPPRIMARYGENRE')
            self.kexp.obscenity = TagAAC('KEXPFCCOBSCENITYRATING')

        
class ID3(object):
    def __init__(self, kexp=False):
        self.kexp = None

        self.mbid = TagID3Text('TXXX:MBID')
        self.mbid_p = TagID3Text('TXXX:MusicBrainz Album Id')
        self.album = TagID3AlbumName('TALB')
        self.album_artist = TagID3AlbumArtist('TPE1')
        self.release_date = TagID3Releasedate('TDRC')

        self.disc_num = TagID3DiscNum('TPOS')
        self.track_num = TagID3TrackNum('TRCK')
        self.title = TagID3TrackTitle('TIT2')
        self.artist = TagID3TrackArtist('TPE2')
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = TagID3Text('TXXX:KEXPPRIMARYGENRE')
            self.kexp.obscenity = TagID3Text('TXXX:KEXPFCCOBSCENITYRATING')

        
class Vorbis(object):
    def __init__(self, kexp=False):
        self.kexp = None
        
        self.mbid = Tag('mbid')
        self.mbid_p = Tag('musicbrainz_albumid')
        self.album = Tag('album')
        self.album_artist = Tag('albumartist')
        self.release_date = Tag('date')

        self.disc_num = Tag('discnumber')
        self.track_num = Tag('tracknumber')
        self.title = Tag('title')
        self.artist = Tag('artist')
        
        if kexp:
            self.kexp = KEXP()
            self.kexp.primary_genre = Tag('KEXPPRIMARYGENRE')
            self.kexp.obscenity = Tag('KEXPFCCOBSCENITYRATING')