import mutagen
from . import AudioTag
from . import Util

class UnsupportedFiletypeError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str(self):
        return str(self.message)

class Length(object):

    def __init__(self, length):
        """
        A tag-like class to encapsulate length (which is not a tag)
        so that it can be treated the same as other tags

        :param length: Length of audio file in seconds
        :return:
        """
        self.value = Util.minutes_seconds(length)
        self.name = "Length"
        self.release = False

        
class MutagenAudioFile(object):

    aac = AudioTag.AAC(True)
    id3 = AudioTag.ID3(True)
    vorbis = AudioTag.Vorbis(True)

    formats = {"aac": aac, "id3": id3, "vorbis": vorbis}

    def __init__(self, file_name):
    
        ############################
        #   switch back around to straight-up?????????
        #   i think this way only helps this class, and this class
        #   is allowed to be messy internally
        ############################
        self.file_name = file_name
        self.mbid, self.album, self.album_artist, self.release_date, self.title, self.artist = None, None, None, None, None, None
        self.disc_num, self.track_num, self.length = None, None, None
        self.label = None
        self.kexp = None
        self.format = None
        self.audio = None
    
        try:
            self.audio = mutagen.File(file_name)
            if not self.audio:
                raise UnsupportedFiletypeError(file_name)
        except IOError as e:
            # if there's an error opening the file with mutagen, return None
            #print("Mutagen IO error: ", e)
            raise e

        format = None
        for type in self.audio.mime:
            if type in AudioTag.Formats.mime_map:
                format = AudioTag.Formats.mime_map[type]
                break

        if not format:
            # we can not process this audio file type; raise an error
            raise UnsupportedFiletypeError(file_name)
        else:
            tags = self.audio.tags
            self.format = self.formats[format]
            format = self.format
            
            # fill in basic metadata
            self.mbid = format.mbid(tags)
            self.album = format.album(tags)
            self.album_artist = format.album_artist(tags)
            self.release_date = format.release_date(tags)   
            self.label = format.label(tags)
            
            self.disc_num = format.disc_num(tags)
            self.track_num = format.track_num(tags)
            self.title = format.title(tags)
            self.artist = format.artist(tags)
            
            self.kexp = self.KEXP()
                
            self.length = Length(self.audio.info.length)
        
    def KEXP(self):
        if not self.kexp:
            self.kexp = KEXP(self.audio, self)
            
        return self.kexp

    def __save_tag__(self, tag):
        """
        :return: True if self.audio's tags have been changed,
        False otherwise
        """
        tag_set = False
        
        print(ascii(tag.tag_name))
        
        if tag.value:
            tag_value = tag.format()
            self.audio[tag.tag_name] = tag_value
            tag_set = True
        elif tag.tag_name in self.audio.tags:
            self.audio.pop(tag.tag_name)
            tag_set = True

        return tag_set
        
    def save_mbid(self, mbid):
        self.mbid.value = mbid
        self.__save_tag__(self.mbid)
        self.audio.save()
        
    def save_album(self, album):
        self.album.value = album
        self.__save_tag__(self.album)
        self.audio.save()
        
    def save_album_artist(self, album_artist):
        self.album_artist.value = album_artist
        self.__save_tag__(self.album_artist)
        self.audio.save()
        
    def save_release_date(self, release_date):
        self.release_date.value = release_date
        self.__save_tag__(self.release_date)
        self.audio.save()

    def save_disc_num(self, disc_num):
        self.disc_num.value = disc_num
        self.__save_tag__(self.disc_num)
        self.audio.save()
       
    def save_track_num(self, track_num):
        self.track_num.value = track_num
        self.__save_tag__(self.track_num)
        self.audio.save()
        
    def save_title(self, title):
        self.title.value = title
        self.__save_tag__(self.title)
        self.audio.save()
        
    def save_artist(self, artist):
        self.artist.value = artist
        self.__save_tag__(self.artist)
        self.audio.save()
        
    def save_label(self, label):
        self.label.value = label
        self.__save_tag__(self.label)
        self.label.save()

    def save(self):
        """
        Save any changes to metadata in the AudioFile object
        to the audio file it represents
        """
        
        # set all elements in the mutagen File object
        self.__save_tag__(self.mbid)
        self.__save_tag__(self.album)
        self.__save_tag__(self.album_artist)
        self.__save_tag__(self.release_date)
        self.__save_tag__(self.disc_num)
        self.__save_tag__(self.track_num)
        self.__save_tag__(self.title)
        self.__save_tag__(self.artist)
        self.__save_tag__(self.label)
        
        # set KEXP attributes
        if self.kexp:
            self.__save_tag__(self.kexp.primary_genre)
            self.__save_tag__(self.kexp.obscenity)
            
        self.audio.save()

    def as_dict(self):
        as_dict = {"MBID": self.mbid, "Label": self.label, "Album": self.album, "Album Artist": self.album_artist,
                        "Year": self.release_date, "Title": self.title, "Artist": self.artist,
                        "Disc Num": self.disc_num, "Track Num": self.track_num, "Length": self.length}

        if self.kexp:
            as_dict["KEXP Primary Genre"] = self.kexp.primary_genre
            as_dict["KEXPFCCOBSCENITYRATING"] = self.kexp.obscenity
        return as_dict

    def __iter__(self):
        it = AudioFileIterator(self)
        return it
        
        
class AudioFileIterator():

    ordering = ["Album Artist", "Album", "Label", "Disc Num", "Year", "MBID",
                "Track Num", "Title", "Artist", "Length", "KEXPFCCOBSCENITYRATING"]

    def __init__(self, audiofile):
        self.as_dict = audiofile.as_dict()
                
        self.index = 0
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.ordering):
            raise StopIteration
        key = self.ordering[self.index]
        next = (key, self.as_dict[key])
        self.index += 1
        return next


class KEXP(object):
    def __init__(self, audio, audio_file):
        """
        Extract and save KEXP-specific metadata from an audio file.

        :param audio: mutagen.File() object
        :param format: Audio format
        :return:
        """
        self.format = audio_file.format
        self.__save_tag__ = audio_file.__save_tag__
        self.audio = audio
        
        self.primary_genre = None
        self.obscenity = None
        
        tags = audio.tags
        
        self.obscenity = self.format.kexp.obscenity(tags)
        self.primary_genre = self.format.kexp.primary_genre(tags)

    def save_primary_genre(self, primary_genre):
        self.primary_genre.value = primary_genre
        self.__save_tag__(self.primary_genre)
        self.audio.save()
        
    def save_obscenity(self, obscenity):
        self.obscenity.value = obscenity
        self.__save_tag__(self.obscenity)
        self.audio.save()


class AudioFile:

    def __init__(self, audiofile = MutagenAudioFile):
        self.audiofile = audiofile
        self.audiofiles = dict()
        
    def get(self, file_name):
        if file_name in self.audiofiles:
            return self.audiofiles[file_name]
        else:
            af = self.audiofile(file_name)
            self.audiofiles[file_name] = af
            return af