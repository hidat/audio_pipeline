from audio_pipeline.util import AudioFile


class KEXPCustomTags:
    anchor = "KEXPAnchorStatus"
    radio_edit = "KEXPRadioEdit"


class KEXPAudioFile(AudioFile.BaseAudioFile):

    def __init__(self, file_name):
        super().__init__(file_name)
        
    @property
    def anchor(self):
        return self._get_custom_tag_(KEXPCustomTags.anchor)

    @anchor.setter
    def anchor(self, val):
        self._set_custom_tag_(KEXPCustomTags.anchor, val)
    
    @property
    def KEXPRadioEdit(self):
        return self._get_custom_tag_(KEXPCustomTags.radio_edit)

    @KEXPRadioEdit.setter
    def KEXPRadioEdit(self, val):
        self._set_custom_tag_(KEXPCustomTags.radio_edit, val)

    def track(self):
        track = super().track()
        track += [self.anchor, self.KEXPRadioEdit]
        return track