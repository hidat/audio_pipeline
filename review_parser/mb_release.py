import json
import os
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

class MBTrack:
    def __init__(self, jsonDict):
        if jsonDict is not None:
            self.trackNum = jsonDict['track_num']
            self.title = jsonDict['track_name']
            self.itemCode = jsonDict['item_code']

###
# Finds all directories under the given directory that match  'review_json_log_*', reading in the release and track
# logs under each directory.
###
def readAllLogs(dirname):
    releases = []
    files = os.listdir(dirname)
    for file in files:
        fullName = path.join(dirname, file)
        if path.isdir(fullName) and file.startswith('review_json_log_'):
            releases.extend(readReleaseLog(fullName))
    return releases


###
# Reads the given release log, creating a array of MBRelease  objects
###
def readReleaseLog(dirname):
    releases = []
    tracksDirectory = path.join(dirname, 'tracks')
    filename = path.join(dirname, 'releases.json')
    if path.isfile(filename):
        fp = open(filename)
        for rs in fp:
            parsedRelease = json.loads(rs)
            if parsedRelease is not None:
                release = MBRelease(parsedRelease)

                # Try and find the associated tracks log
                trackLog = path.join(tracksDirectory, release.mbID + '.json')
                release.tracks = readTrackLog(trackLog)

                releases.append(release)

    return releases

def readTrackLog(filename):
    tracks = {}
    if path.isfile(filename):
        fp = open(filename)
        for rs in fp:
            parsedTracks = json.loads(rs)
            if parsedTracks is not None:
                track = MBTrack(parsedTracks)
                tracks[track.trackNum] = track

    return tracks