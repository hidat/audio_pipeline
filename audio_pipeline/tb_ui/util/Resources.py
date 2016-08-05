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
    d = os.path.split(directory)[1]
    track = False
    # we'll set this to a DBPOWERAMP config later

    #if InputPatterns.release_pattern.match(d):

    for f in os.scandir(directory):
        if f.is_file:
            file_name = f.name

            try:
                track = AudioFileFactory.get(f.path)
            except IOError:
                track = False
                continue
            except Exceptions.UnsupportedFiletypeError:
                track = False
                continue
            break
    return track
