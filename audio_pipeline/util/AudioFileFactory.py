from . import AudioFile
from . import KEXPAudioFile


class AudioFileFactory:

    audiofile = AudioFile.BaseAudioFile
    audiofiles = dict()
 
    audiofile_options = {"kexp": KEXPAudioFile.KEXPAudioFile} 

    @classmethod
    def get(cls, file_name):
        if file_name in cls.audiofiles:
            return cls.audiofiles[file_name]
        else:
            af = cls.audiofile(file_name)
            cls.audiofiles[file_name] = af
            return af
            
    @classmethod
    def set(cls, audiofile_type):
        audiofile_type = audiofile_type.casefold()
        if audiofile_type in cls.audiofile_options:
            cls.audiofile = cls.audiofile_options[audiofile_type]
            return True
            
        return False