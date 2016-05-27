import uuid
import configparser
import os

        
def minutes_seconds(length):
    # turns a floating point value into a string of (approximate)
    # minutes : seconds
    # assuming its just in seconds to start
    raw = length / 60
    minutes = int(raw)
    seconds = int((raw - minutes) * 60)
    if seconds < 10:
        seconds = "0" + str(seconds)
    final = str(minutes) + ":" + str(seconds)
    return final

    
def seconds(min_sec):
    min, sec = min_sec.split(":")
    seconds = int(min) * 60 + int(sec)
    return seconds

    
class Obscenity:
    red = "RED DOT"
    yellow = "YELLOW DOT"
    clean = "CLEAN EDIT"
    

def is_mbid(id):
    """
    Check that 's' looks like an MBID
    """
    try:
        id = uuid.UUID(id)
        good = True
    except ValueError as e:
        good = False    
    
    return good
    
def has_mbid(track):
    """
    Check whether or not the given track has an MBID.
    """
    
    if track.mbid.value:
        good = is_mbid(track.mbid.value)
    else:
        good = False
        
    return good