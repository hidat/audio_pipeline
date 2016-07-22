import json
import os.path as path
import unicodedata


###
# Manages reading a MusicBrainz release from a JSON file.  These files are assumed to have been created by the
# audio-pipelines JsonSerializer as part of the FileWalker process
###
class MBRelease:
    def __init__(self, jsonDict):
        if jsonDict is not None:
            self.mbID = jsonDict['item_code']
            self.title = jsonDict['name']
            self.normalizedTitle = unicodedata.normalize('NFKC', self.title).replace(u'\u2013', '-').casefold()
            self.artist = jsonDict['artist']
            self.normalizedArtist = unicodedata.normalize('NFKC', self.artist).replace(u'\u2013', '-').casefold()
            self.daletGlossaryName = jsonDict['glossary_title']
            if 'tracks' in jsonDict:
                self.tracks = jsonDict['tracks']

###
# Reads the given release log, creating a array of MBRelease  objects
###
def readReleaseLog(filename):
    releases = []
    if path.isfile(filename):
        fp = open(filename)
        for rs in fp:
            parsedRelease = json.loads(rs)
            if parsedRelease is not None:
                release = MBRelease(parsedRelease)
                releases.append(release)
    return releases
