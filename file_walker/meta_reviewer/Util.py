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
    
    
class MetaAttributes():
    # TODO: Make this a properly subscriptable class, instead of... whatever's going on here
    def __init__(self):
        self.mbid = FormatMeta("mbid", '----:com.apple.iTunes:MBID', 'TXXX:MBID')
        self.pmbid = FormatMeta("musicbrainz_albumid", '----:com.apple.iTunes:MusicBrainz Album Id', 'TXXX:MusicBrainz Album Id')
        self.kexp_genre = FormatMeta("KEXPPRIMARYGENRE", '----:com.apple.iTunes:KEXPPRIMARYGENRE',  'TXXX:KEXPPRIMARYGENRE')
        self.obscenity_rating = FormatMeta("KEXPFCCOBSCENITYRATING", '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING', 'TXXX:KEXPFCCOBSCENITYRATING')
        self.album = FormatMeta("album", "\xa9alb", 'ALBUM')
        self.albumartist = FormatMeta("albumartist", "\aART", "TPE1")
        self.tracknumber = FormatMeta("tracknumber", 'trkn', 'TRCK')
        self.discnumber = FormatMeta("discnumber", "disk", "TPOS")
        self.title = FormatMeta("title", '\xa9nam', 'TIT2')
        self.trackartist = FormatMeta("artist", '\xa9ART', 'TPE2')
        
        self.album_attributes = [self.mbid, self.pmbid, self.album, self.albumartist]
        self.track_attributes = [self.tracknumber, self.discnumber, \
                                 self.title, self.trackartist, self.kexp_genre]
                                 
    def add_tag(self, tag_name, vorbis, aac, id3):
        self.tag_name = FormatMeta(vorbis, aac, id3)
        
        
class FormatMeta():
    
    def __init__(self, vorbis, aac, id3):
        self.vorbis = vorbis
        self.aac = aac
        self.id3 = id3