from audio_pipeline import Constants


class AudioFileFactory:

    audiofiles = dict()

    @classmethod
    def get(cls, file_name):
        if file_name in cls.audiofiles:
            return cls.audiofiles[file_name]
        else:
            af = Constants.audiofile(file_name)
            cls.audiofiles[file_name] = af
            return af