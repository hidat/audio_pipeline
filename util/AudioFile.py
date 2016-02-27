import os
import mutagen
import audio_pipeline.util.AudioTag as AudioTag


class UnsupportedFiletypeError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str(self):
        return str(self.message)


class AudioFile(object):

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
        self.mbid, self.album, self.album_artist, self.release_date, self.title, self.artist = None, None, None, None, None, None
        self.disc_num, self.track_num, self.length = None, None, None
        self.kexp = None
        self.format = None
        self.audio = None
    
        try:
            self.audio = mutagen.File(file_name)
            if not self.audio:
                raise UnsupportedFiletypeError(file_name)
        except IOError as e:
            # if there's an error opening the file with mutagen, return None
            print("Mutagen IO error: ", e)
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
            
            self.disc_num = format.disc_num(tags)
            self.track_num = format.track_num(tags)
            self.title = format.title(tags)
            self.artist = format.artist(tags)
                
            self.kexp = self.KEXP()
                
            self.length = self.audio.info.length
            
        
    def KEXP(self):
        if not self.kexp:
            self.kexp = KEXP(self.audio, self.format)
            
        return self.kexp
    
    
    def __save_tag__(self, tag):
        """
        :return: True if self.audio's tags have been changed,
        False otherwise
        """
        set = False
    
        if tag.name in self.audio.tags or tag_value > 0:
            tag_value = tag.format()
            self.audio[tag.name] = tag_value
            set = True
            
        return set

        
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
        self.__save_tag__(tag, track_num)
        self.audio.save()
        
        
    def save_artist(self, artist):
        self.artist.value = artist
        self.__save_tag__(self.artist)
        self.audio.save()
        

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
        self.__save_tag__(self.artist)
        
        # set KEXP attributes
        if self.kexp:
            self.__save_tag__(self.kexp.primary_genre)
            self.__save_tag__(self.kexp.obscenity_rating)
            
        self.audio.save()



class KEXP(object):
    def __init__(self, audio, format):
        """
        Extract and save KEXP-specific metadata from an audio file.

        :param audio: mutagen.File() object
        :param format: Audio format
        :return:
        """
        self.format = format
        self.audio = audio
        
        self.primary_genre = None
        self.obscenity = None
        
        tags = audio.tags
        
        self.obscenity = format.obscenity(tags)
        self.primary_genre = primary_genre.(tags)
            
    def __save_tag__(self, tag):
        """
        :return: True if self.audio's tags have been changed,
        False otherwise
        """
        set = False
    
        if tag.name in self.audio.tags or tag_value > 0:
            tag_value = tag.format()
            self.audio[tag.name] = tag_value
            set = True
            
        return set

            
    def save_primary_genre(self, primary_genre):
        self.__save_tag__(self.primary_genre)
        self.audio.save()
        
    def save_obscenity_rating(self, obscenity):
        self.__save_tag__(self.obscenity)
        self.audio.save()

        