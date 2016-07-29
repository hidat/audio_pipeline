import uuid
import unicodedata
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

    
class Edits:
    radio_edit = "RADIO EDIT"
    kexp_edit = "KEXP RADIO EDIT"
    
    
class Obscenity:
    red = "RED DOT"
    yellow = "YELLOW DOT"
    clean = "CLEAN EDIT"
    kexp_clean = "KEXP CLEAN EDIT"
    

def is_mbid(id):
    """
    Check that 's' looks like an MBID
    """
    try:
        id = uuid.UUID(id)
        good = True
    except ValueError as e:
        good = False
    except AttributeError:
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

    
def distRuleCleanup(rule):
    cleanRule = rule
    if not rule.isalpha():
        cleanRule = '#'
    else:
        rule = unicodedata.normalize('NFKD', rule).encode('ascii', 'ignore').decode()
        if len(rule) > 0:
            cleanRule = rule
    return cleanRule


def stringCleanup(text):
    clean = {'\\': '-', '/': '-', '\"': '\''}
    for character, replacement in clean.items():
        text = text.replace(character, replacement)
    return text