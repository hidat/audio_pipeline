import os
import mutagen

class FileMeta(object):
    def __init__(self, KEXP=False):
        self.aac = TagFormat.AAC(KEXP)
        self.id3 = TagFormat.ID3(KEXP)
        self.vorbis = TagFormat.Vorbis(KEXP)
