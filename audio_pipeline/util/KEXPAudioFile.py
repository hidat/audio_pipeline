from . import AudioFile


class Tags:
    obscenity = "KEXPFCCOBSCENITYRATING"
    category = "KEXPPRIMARYGENRE"
    anchor = "KEXPAnchorStatus"
    radio_edit = "KEXPRadioEdit"


class KEXPAudioFile(AudioFile.BaseAudioFile):

    def __init__(self, file_name):
        super().__init__(file_name)

        self.obscenity = self.format.custom_tag(Tags.obscenity, self.audio)
        self.category = self.format.custom_tag(Tags.category, self.audio)
        self.anchor = self.format.custom_tag(Tags.anchor, self.audio)
        self.radio_edit = self.format.custom_tag(Tags.anchor, self.audio)

    def track(self):
        track = super().track()
        track += [self.obscenity, self.category, self.anchor, self.radio_edit]
        return track


t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?', 'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)', 'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004 04 19', 'date2': '2004', 'source': 'CD (Lossless)', 'discnumber': 1, 'accurateripdiscid': '012-0011f4ba-00a8233b-8809700c-4', 'batchid': '50024', 'encoded by': 'dBpoweramp Release 14.4', 'title': 'Confusion', 'accurateripresult': 'AccurateRip: Accurate (confidence 62)   [37DEB629]',  'artist': 'The Zutons', 'tracknumber': 4, 'disctotal': 1, 'genre': 'Rock', 'mbid': '5560ffa9-3824-44f4-b2bf-a96ae4864187', 'length': '3:32'}
