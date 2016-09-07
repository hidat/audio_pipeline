from audio_pipeline.util import AudioFile


class CustomTags:
    obscenity = "KEXPFCCOBSCENITYRATING"
    category = "KEXPPRIMARYGENRE"
    anchor = "KEXPAnchorStatus"
    radio_edit = "KEXPRadioEdit"
    secondary_genre = 'KEXPSecondaryGenre'


class KEXPAudioFile(AudioFile.BaseAudioFile):

    def __init__(self, file_name):
        super().__init__(file_name)

        self.obscenity = self.format.custom_tag(CustomTags.obscenity, self.audio)
        self.category = self.format.custom_tag(CustomTags.category, self.audio)
        self.anchor = self.format.custom_tag(CustomTags.anchor, self.audio)
        self.radio_edit = self.format.custom_tag(CustomTags.radio_edit, self.audio)
        self.secondary_genre = self.format.custom_tag(CustomTags.secondary_genre, self.audio)

    def track(self):
        track = super().track()
        track += [self.obscenity, self.radio_edit, self.category, self.anchor, self.secondary_genre]
        return track

    def tb_track(self):
        track = super().tb_track()
        track += [{'width': self.default_track_width, 'tag': self.obscenity},
                  {'width': self.default_track_width, 'tag': self.radio_edit},
                  {'width': self.default_track_width, 'tag': self.secondary_genre}]
        return track