from audio_pipeline.util import AudioFile


class CustomTags:
    obscenity = "KEXPFCCOBSCENITYRATING"
    category = "KEXPPRIMARYGENRE"
    anchor = "KEXPAnchorStatus"
    radio_edit = "KEXPRadioEdit"


class KEXPAudioFile(AudioFile.BaseAudioFile):

    def __init__(self, file_name):
        super().__init__(file_name)

        self.obscenity = self.format.custom_tag(CustomTags.obscenity, self.audio)
        self.category = self.format.custom_tag(CustomTags.category, self.audio)
        self.anchor = self.format.custom_tag(CustomTags.anchor, self.audio)
        self.radio_edit = self.format.custom_tag(CustomTags.radio_edit, self.audio)

    def track(self):
        track = super().track()
        track += [self.obscenity, self.radio_edit, self.category, self.anchor]
        return track