import uuid


mbid_directory = "Ready To Filewalk"
picard_directory = "Picard Me!"

cache_limit = 30

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