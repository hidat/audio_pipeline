import mutagen.id3
import re
import abc

class BaseFormats(object):
    
    __formats__ = []    # supported metadata tagging formats
    __file_ext__ = []   # supported file type extensions
    __ext_mapping__ = {}
    
    @classmethod
    def formats(cls):
        return cls.__formats__.copy()
        
    @classmethod
    def extensions(cls):
        return cls.__file_ext__.copy()
        
    @classmethod
    def ext_to_format(cls):
        return cls.__ext_mapping__.copy()

    
class Formats(BaseFormats):
    
    aac = "aac"
    id3 = "id3"
    vorbis = "vorbis"
    
    mp4 = ".mp4"
    m4a = ".m4a"
    mp3 = ".mp3"
    flac = ".flac"
    
    __formats__ = [aac, id3, vorbis]    # supported metadata tagging formats
    __file_ext__ = [mp4, m4a, mp3, flac]   # supported file type extensions
    
    __ext_mapping__ = {mp4: aac, m4a: aac, mp3: id3, flac: vorbis}


class Tag(object):
    # currently only keeps track of a tag name
    # but should keep track of type & format of value in the future
    
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
        
    

class SimpleTags:

    def __init__(self, add_attr = {}):
        """
        Allows simplified access to metadata tags in multiple tagging styles.
        
        Current supported styles: ID3v2.4, AAC with iTunes-style tagging,
        Vorbis comments as dBPoweramp applies them.
        
        :param add_attr: Additional attributes to add upon object creation. Each attribute must be of the format
            general_tag_name: {'vorbis': vorbis_tag_name, 'aac': iTunes_aac_tag_name, 'id3': id3v2.4_tag_name, 'frame': id3v2.4_tag_frame}
            OR
            general_tag_name: TagFormat
        """
        
        self.formats = ['vorbis', 'aac', 'id3']
        
        mb_txxx = mutagen.id3.TXXX(encoding=3)
        mb_txxx.desc = "MBID"
        mbid = TagFormat("mbid", "mbid", '----:com.apple.iTunes:MBID', 'TXXX:MBID', mb_txxx)
        picard_mbid = TagFormat("mbid", "musicbrainz_albumid", '----:com.apple.iTunes:MusicBrainz Album Id', 'TXXX:MusicBrainz Album Id', mb_txxx)
        genre_txxx = mutagen.id3.TXXX(encoding=3)
        genre_txxx.desc = "KEXPPRIMARYGENRE"
        kexp_genre = TagFormat("kexp_genre", "KEXPPRIMARYGENRE", '----:com.apple.iTunes:KEXPPRIMARYGENRE',  'TXXX:KEXPPRIMARYGENRE', genre_txxx)
        obscenity_txxx = mutagen.id3.TXXX(encoding=3)
        obscenity_txxx.desc = "KEXPFCCOBSCENITYRATING"
        obscenity_rating = TagFormat("obscenity_rating", "KEXPFCCOBSCENITYRATING", '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING', 'TXXX:KEXPFCCOBSCENITYRATING', obscenity_txxx)
        talb = mutagen.id3.TALB(encoding=3)
        album = TagFormat("album", "album", '\xa9alb', 'TALB', talb)
        tpe1 = mutagen.id3.TPE1(encoding=3)
        album_artist = TagFormat("album_artist", "albumartist", '\aART', "TPE1", tpe1)
        trck = mutagen.id3.TRCK(encoding=3)
        track_num = TagFormat("track_num", "tracknumber", 'trkn', 'TRCK', trck)
        tpos = mutagen.id3.TPOS(encoding=3)
        disc_num = TagFormat("disc_num", "discnumber", "disk", 'TPOS', tpos)
        tit2 = mutagen.id3.TIT2(encoding=3)
        track_title = TagFormat("title", "title", '\xa9nam', 'TIT2', tit2)
        tpe2 = mutagen.id3.TPE2(encoding=3)
        track_artist = TagFormat("artist", "artist", '\xa9ART', 'TPE2', tpe2)
        
        self.attributes = {'mbid': mbid, 'pmbid': picard_mbid, 'album': album, \
                           'albumartist': album_artist, 'tracknum': track_num, 'discnum': disc_num, \
                           'title': track_title, 'artist': track_artist, 'kexp_genre': kexp_genre, \
                           'obscenity': obscenity_rating}
                           
        # if len(add_attr) > 0:
            # for tag_name, format_info in add_attr.items():
                # if type(format_info) is TagFormat:
                    # self.attributes[tag_name] = format_info
                # else:
                    # # Do some sanity checks & put tag information into a TagFormat object
                    # if type(format_info) is dict:
                        
                    
                           
    def add_tag(self, tag_name, vorbis, aac, id3):
        self.attributes[tag_name] = TagFormat(tag_name, vorbis, aac, id3)

    def __getitem__(self, item):
        item = item.casefold()
        if re.match('music(\s*_*)*brainz(\s*_*)*(album)*id', item):
            return self.attributes['pmbid']
        elif re.match('album(\s*_*)*artist', item):
            return self.attributes('albumartist')
        elif re.match('(track)*\s*_*artist', item):
            return self.attribute['artist']
        elif re.match('(track\s*_*name)|(track*\s*_*title)', item):
            return self.attribute['title']
        elif re.match('(kexp)*(fcc)*obscenity\s*_*(rating)*', item):
            return self.attributes['obscenity']
        elif item in self.attributes.keys():
            return(self.attributes[item])

class TagFormat:

    def __init__(self, tag, vorbis, aac, id3_tag, id3_frame):
        self.tag = tag
        self.vorbis = vorbis
        self.aac = aac
        self.id3_tag = id3_tag
        self.id3_frame = id3_frame

    def __getitem__(self, item):
        if item.casefold() in ['aac', '.m4a']:
            return self.aac
        elif item.casefold() in ['id3', '.mp3']:
            return self.id3_tag
        elif item.casefold() in ['.flac', 'vorbis']:
            return self.vorbis
        elif item.casefold() in ['tag', 'tag_name', 'tagname', 'value']:
            return self.tag
        elif item.casefold() in ['id3_frame', 'frame']:
            return self.id3_frame