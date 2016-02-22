import os
import mutagen
import AudioTag

class UnsupportedFileTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class AudioFile(object):

    kexp = True

    aac = AudioTag.AAC(kexp)
    id3 = AudioTag.ID3(kexp)
    vorbis = AudioTag.Vorbis(kexp)

    formats = {"aac": aac, "id3": id3, "vorbis": vorbis}

    def __init__(self, file_name, KEXP=True):
        if KEXP != self.kexp:
            global kexp
            kexp = KEXP
            global aac
            aac = AudioTag.AAC(kexp)
            global id3
            id3 = AudioTag.ID3(kexp)
            global vorbis
            vorbis = AudioTag.Vorbis(kexp)

        try:
            audio = mutagen.File(file_name)
        except IOError as e:
            # if there's an error opening the file with mutagen, return None
            print("Mutagen IO error: ", e)
            return None

        format = None
        for type in audio.mime:
            if type in AudioTag.Formats.mime_map:
                format = AudioTag.formats.mime_map[format]
                break

        if not format:
            # we can not process this audio file type; raise exception
            raise UnsupportedFileTypeError(file_name)
        else:





class KEXP(object):
    def __init__(self, audio_file):
        """
        KEXP-specific metadata extracted from the audio file.

        :param audio_file: AudioFile object of the audio file.
        :return:
        """

