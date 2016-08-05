import uuid
import os
from audio_pipeline.util.AudioFileFactory import AudioFileFactory
from audio_pipeline.util import Exceptions


mbid_directory = "Ready To Filewalk"
picard_directory = "Picard Me!"

cache_limit = 30

cancel = -1
checked = 1
unchecked = 0

def has_mbid(track):
    """
    Check whether or not the given track has an MBID.
    """
    
    if track.mbid.value:
        try:
            id = uuid.UUID(track.mbid.value)
            good = True
        except ValueError as e:
            good = False
    else:
        good = False
        
    return good


def is_release(directory):
    track = False
    # we'll set this to a DBPOWERAMP config later

    #if InputPatterns.release_pattern.match(d):

    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        if os.path.isfile(file_path):

            try:
                track = AudioFileFactory.get(file_path)
            except IOError:
                track = False
                continue
            except Exceptions.UnsupportedFiletypeError:
                track = False
                continue
            break
    return track
