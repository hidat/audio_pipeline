import os
import mutagen
import AudioTag


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
        self._kexp = None
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
            # we can not process this audio file type; return None
            raise UnsupportedFiletypeError(file_name)
        else:
            tags = self.audio.tags
            self.format = self.formats[format]
            format = self.format
            
            # fill in basic metadata
            mbid = format.mbid
            mbid_p = format.mbid_p
            if mbid.name in tags:
                self.mbid = mbid.extract(tags[mbid.name])
            elif mbid_p.name in tags:
                self.mbid = mbid_p.extract(tags[mbid_p.name])
            else:
                self.mbid = ''

            album = format.album
            if album.name in tags:
                self.album = album.extract(tags[album.name])
            album_artist = format.album_artist
            if album_artist.name in tags:
                self.album_artist = album_artist.extract(tags[album_artist.name])
            release_date = format.release_date
            if release_date.name in tags:
                self.release_date = release_date.extract(tags[release_date.name])
                
            disc_num = format.disc_num
            if disc_num.name in tags:
                self.disc_num = int(disc_num.extract(tags[disc_num.name]))
            track_num = format.track_num
            if track_num.name in tags:
                self.track_num = int(track_num.extract(tags[track_num.name]))
            title = format.title
            if title.name in tags:
                self.title = title.extract(tags[title.name])
            artist = format.artist
            if artist.name in tags:
                self.artist = artist.extract(tags[title.name])
                
            self._kexp = KEXP(self)
                
            self.length = self.audio.info.length
            
        
    def kexp(self):
        if not self._kexp:
            self._kexp = KEXP(self)
            
        return self._kexp
    
    
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
        if self._kexp:
            tag = self.format.kexp_genre
            self.__save_tag__(tag, self._kexp.primary_genre)
            tag = self.format.kexp_obscenity
            self.__save_tag__(tag, self._kexp.obscenity_rating)
            
        self.audio.save()



class KEXP(object):
    def __init__(self, audio_file):
        """
        KEXP-specific metadata extracted from the audio file.

        :param audio_file: AudioFile object of the audio file.
        :return:
        """
        format = audio_file.format
        tags = audio_file.audio.tags
        
        self.primary_genre = ''
        self.obscenity_rating = ''
        
        obscenity_rating = format.kexp_obscenity
        if obscenity_rating.name in tags:
            self.obscenity_rating = obscenity_rating.extract(tags[obscenity_rating.name])
        
        primary_genre = format.kexp_genre
        if primary_genre.name in tags:
            self.primary_genre = primary_genre.extract(tags[primary_genre.name])
        