from audio_pipeline import Constants


class AudioFileFactory:

    audiofiles = dict()

    @classmethod
    def get(cls, file_name):
        if file_name in cls.audiofiles:
            return cls.audiofiles[file_name]
        else:
            af = Constants.audiofile(file_name, Constants.custom_release_tags, Constants.custom_track_tags,
                                     Constants.tb_release_tags, Constants.tb_track_tags)
            cls.audiofiles[file_name] = af
            return af