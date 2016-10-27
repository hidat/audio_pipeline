from audio_pipeline.util import AudioFile

class CustomTags:
    obscenity = "KEXPFCCOBSCENITYRATING"
    category = "KEXPPRIMARYGENRE"
    anchor = "KEXPAnchorStatus"
    radio_edit = "KEXPRadioEdit"
    secondary_genre = 'KEXPSecondaryGenre'


class KEXPAudioFile(AudioFile.BaseAudioFile):

    def __init__(self, file_name, release_tags=None, track_tags=None):
        super().__init__(file_name, release_tags, track_tags)

        self.obscenity = self.format.custom_tag(CustomTags.obscenity, self.audio)
        self.category = self.format.custom_tag(CustomTags.category, self.audio)
        self.anchor = self.format.custom_tag(CustomTags.anchor, self.audio)
        self.radio_edit = self.format.custom_tag(CustomTags.radio_edit, self.audio)
        self.secondary_genre = self.format.custom_tag(CustomTags.secondary_genre, self.audio)

    def track(self):
        track = super().track()
        track += [self.obscenity, self.radio_edit, self.category, self.anchor]
        return track

    def release(self):
        release = super().release()
        release += [self.secondary_genre]
        return release

    def tb_track(self):
        track = super().tb_track()
        TBTag = AudioFile.collections.namedtuple("TBTag", ["width", "tag"])

        track += [TBTag(self.default_track_width, self.obscenity),
                  TBTag(self.default_track_width, self.radio_edit)]
        return track

    def tb_release(self):
        release = super().tb_release()
        TBTag = AudioFile.collections.namedtuple("TBTag", ["width", "row", "tag"])

        release += [TBTag(self.default_release_width, 1, self.secondary_genre)]
        return release