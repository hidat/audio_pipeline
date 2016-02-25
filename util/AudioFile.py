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
        self.mbid, self.album, self.album_artist, self.release_date, self.title, self.artist = '', '', '', '', '', ''
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
            mbid = format.mbid
            mbid_p = format.mbid_p
            if mbid.name in tags:
                self.mbid = mbid.extract_str(tags[mbid.name])
            elif mbid_p.name in tags:
                self.mbid = mbid_p.extract_str(tags[mbid_p.name])
            else:
                self.mbid = ''

            album = format.album
            if album.name in tags:
                self.album = album.extract_str(tags[album.name])
            album_artist = format.album_artist
            if album_artist.name in tags:
                self.album_artist = album_artist.extract_str(tags[album_artist.name])
            release_date = format.release_date
            if release_date.name in tags:
                self.release_date = release_date.extract_str(tags[release_date.name])
                
            disc_num = format.disc_num
            if disc_num.name in tags:
                self.disc_num = int(disc_num.extract_int(tags[disc_num.name]))
            track_num = format.track_num
            if track_num.name in tags:
                self.track_num = int(track_num.extract_int(tags[track_num.name]))
            title = format.title
            if title.name in tags:
                self.title = title.extract_str(tags[title.name])
            artist = format.artist
            if artist.name in tags:
                self.artist = artist.extract_str(tags[artist.name])
                
            self.kexp = self.KEXP()
                
            self.length = self.audio.info.length
            
        
    def KEXP(self):
        if not self.kexp:
            self.kexp = KEXP(self.audio, self.format)
            
        return self.kexp
    
    
    def __save_tag__(self, tag, tag_value):
        """
        :return: True if self.audio's tags have been changed,
        False otherwise
        """
        set = False
    
        if tag.name in self.audio.tags or tag_value > 0:
            tag_value = tag.format(tag_value)
            self.audio[tag.name] = tag_value
            set = True
            
        return set

        
    def save_mbid(self, mbid):
        tag = self.format.mbid
        self.__save_tag__(tag, mbid)
        self.audio.save()
        
        
    def save_album(self, album):
        tag = self.format.album
        self.__save_tag__(tag, album)
        self.audio.save()
        
        
    def save_album_artist(self, album_artist):
        tag = self.format.album_artist
        self.__save_tag__(tag, album_artist)
        self.audio.save()
        
        
    def save_release_date(self, release_date):
        tag = self.format.release_date
        self.__save_tag__(tag, release_date)
        self.audio.save()
        

    def save_disc_num(self, disc_num):
        tag = self.format.disc_num
        self.__save_tag__(tag, disc_num)
        self.audio.save()
        
       
    def save_track_num(self, track_num):
        tag = self.format.track_num
        self.__save_tag__(tag, track_num)
        self.audio.save()
        
        
    def save_artist(self, artist):
        tag = self.format.artist
        self.__save_tag__(tag, artist)
        self.audio.save()
        

    def save(self):
        """
        Save any changes to metadata in the AudioFile object
        to the audio file it represents
        """
        
        # set all elements in the mutagen File object
        tag = self.format.mbid
        self.__save_tag__(tag, self.mbid)
        tag = self.format.album
        self.__save_tag__(tag, self.album)
        tag = self.format.album_artist
        self.__save_tag__(tag, self.album_artist)
        tag = self.format.release_date
        self.__save_tag__(tag, self.release_date)
        tag = self.format.disc_num
        self.__save_tag__(tag, self.disc_num)
        tag = self.format.track_num
        self.__save_tag__(tag, self.track_num)
        tag = self.format.artist
        self.__save_tag__(tag, self.artist)
        
        # set KEXP attributes
        if self.kexp:
            tag = self.format.kexp.primary_genre
            self.__save_tag__(tag, self.kexp.primary_genre)
            tag = self.format.kexp.obscenity
            self.__save_tag__(tag, self.kexp.obscenity_rating)
            
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
        
        self.primary_genre = ''
        self.obscenity = ''
        
        tags = audio.tags
        
        obscenity = format.kexp.obscenity
        if obscenity.name in tags:
            self.obscenity = obscenity.extract_str(tags[obscenity_rating.name])
        
        primary_genre = format.kexp.primary_genre
        if primary_genre.name in tags:
            self.primary_genre = primary_genre.extract_str(tags[primary_genre.name])
            
    def __save_tag__(self, tag, tag_value):
        """
        :return: True if self.audio's tags have been changed,
        False otherwise
        """
        set = False
    
        if tag.name in self.audio.tags or tag_value > 0:
            tag_value = tag.format(tag_value)
            self.audio[tag.name] = tag_value
            set = True
            
        return set

            
    def save_primary_genre(self, primary_genre):
        tag = self.format.kexp.primary_genre
        self.__save_tag__(tag, primary_genre)
        self.audio.save()
        
    def save_obscenity_rating(self, obscenity):
        tag = self.format.kexp.obscenity
        self.__save_tag__(tag, obscenity)
        self.audio.save()

        