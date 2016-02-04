import re
import mutagen.mp4 as mp4
import mutagen.id3

file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis", "ERROR_EXT": "ERROR_EXT"}


release_mapping = {"name": "Album", "album_artist": "Album Artist", "disc_num": "Disc"}
track_mapping = {"name": "Title", "artist": "Artist", "track_num": "Track Number", "length": "Length",
                 "KEXPFCCOBSCENITYRATING": "KEXPFCCOBSCENITYRATING"}
                 
commands_list = {"<track_num>[[,][ ]<track_num>...][ ]<meta_command>": "Add the metadata specified by <meta_command> to track <track_num>. <meta_command> is not case-sensitive.\
                  \nMultiple <track_nums> may be specified, separated by \",\" and/or \" \"\
                  \nValid <meta_command>s:\n\tr[ed[ dot]]: RED DOT obscenity rating\
                  \n\ty[ellow[ dot]]: YELLOW DOT obscenity rating\n\tc[lear]: Remove obscenity rating", 
                 "d[one]": "Close this application.",
                 "n[ext]": "Display metadata of next album", "p[[rev]ious]": "Display metadata of previous album"}
                 
example_list = {"<track_num><meta_command>": "7y: Add YELLOW DOT obscenity rating to track 7 of the current album."}

# List of the names of track and release data elements, in the order I want them displayed
track_categories = ["track_num", "name", "artist", "length", "KEXPFCCOBSCENITYRATING"]
release_categories = ["name", "album_artist", "disc_num"]


kexp_tags = {"obscenity": "KEXPFCCOBSCENITYRATING", "genre": "KEXPPRIMARYGENRE"}
kexp_values = {"y": "YELLOW DOT", "r": "RED DOT"}

def minutes_seconds(length):
    # turns a floating point value into a string of (approximate)
    # minutes : seconds
    # assuming its just in seconds to start
    raw = length / 60
    minutes = int(raw)
    seconds = int((raw - minutes) * 60)
    if seconds < 10:
        seconds = "0" + str(seconds)
    final = str(minutes) + ":" + str(seconds)
    return final
    
    
class MetaAttributes:
    def __init__(self, name):
        self.name = name
        txxx = mutagen.id3.TXXX(encoding=3)
        txxx.desc = 'mbid'
        mbid = FormatMeta("mbid", "mbid", '----:com.apple.iTunes:MBID', 'TXXX:MBID', txxx)
        pmbid = FormatMeta("mbid", "musicbrainz_albumid", '----:com.apple.iTunes:MusicBrainz Album Id', 'TXXX:MusicBrainz Album Id', txxx)
        kexp_genre = FormatMeta("kexp_genre", "KEXPPRIMARYGENRE", '----:com.apple.iTunes:KEXPPRIMARYGENRE',  'TXXX:KEXPPRIMARYGENRE', txxx)
        txxx.desc = "KEXPFCCOBSCENITYRATING"
        obscenity_rating = FormatMeta("obscenity_rating", "KEXPFCCOBSCENITYRATING", '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING', 'TXXX:KEXPFCCOBSCENITYRATING', txxx)
        talb = mutagen.id3.TALB(encoding=3)
        album = FormatMeta("album", "album", '\xa9alb', 'TALB', talb)
        tpe1 = mutagen.id3.TPE1(encoding=3)
        albumartist = FormatMeta("album_artist", "albumartist", '\aART', "TPE1", tpe1)
        trck = mutagen.id3.TRCK(encoding=3)
        tracknumber = FormatMeta("track_num", "tracknumber", 'trkn', 'TRCK', trck)
        tpos = mutagen.id3.TPOS(encoding=3)
        discnumber = FormatMeta("disc_num", "discnumber", "disk", 'TPOS', tpos)
        tit2 = mutagen.id3.TIT2(encoding=3)
        title = FormatMeta("title", "title", '\xa9nam', 'TIT2', tit2)
        tpe2 = mutagen.id3.TPE2(encoding=3)
        trackartist = FormatMeta("artist", "artist", '\xa9ART', 'TPE2', tpe2)
        
        self.attributes = {'mbid': mbid, 'pmbid': pmbid, 'album': album, 'albumartist': albumartist, \
                           'tracknum': tracknumber, 'discnum': discnumber, \
                           'title': title, 'artist': trackartist, 'kexp_genre': kexp_genre, \
                           'obscenity': obscenity_rating}
                                 
    def add_tag(self, tag_name, vorbis, aac, id3):
        self.attributes[tag_name] = FormatMeta(tag_name, vorbis, aac, id3)

    def __getitem__(self, item):
        item = item.casefold()
        if re.match('music(\s*_*)*brainz(\s*_*)*(album)*id', item):
            return self.attributes['pmbid']
        elif re.match('album(\s*_*)*artist', item):
            return self.attributes('albumartist')
        elif re.match('(track)*\s*_*artist', item):
            return self.attribute['artist']
        elif re.match('(track)*\s*_*(title|name)', item):
            return self.attribute['title']
        elif re.match('(kexp)*(fcc)*obscenity\s*_*(rating)*', item):
            return self.attributes['obscenity']
        elif item in self.attributes.keys():
            return(self.attributes[item])

        
class FormatMeta:
    
    def __init__(self, tag, vorbis, aac, id3_tag, id3_frame):
        txxx = mutagen.id3.TXXX(encoding=3)
        print(txxx)
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
        elif item.casefold in ['id3_frame', 'frame']:
            return self.id3_frame