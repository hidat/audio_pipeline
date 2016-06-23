import audio_pipeline


class AudioFileFactory:

    audiofiles = dict()

    @classmethod
    def get(cls, file_name):
        if file_name in cls.audiofiles:
            return cls.audiofiles[file_name]
        else:
            af = audio_pipeline.audiofile(file_name)
            cls.audiofiles[file_name] = af
            return af