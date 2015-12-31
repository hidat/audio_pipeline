file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis", "ERROR_EXT": "ERROR_EXT"}

release_categories = {"name": "Album Name", "album_artist": "Album Artist", "disc_name": "Disc Number"}
track_categories = {"name": "Title", "artist": "Artist", "track_num": "Track Number", "length": "Length"}

def minutes_seconds(length):
    # turns a floating point value into a string of (approximate)
    # minutes : seconds
    # assuming its just in seconds to start
    raw = length / 60
    minutes = int(raw)
    seconds = int((raw - minutes) * 60)
    final = str(minutes) + ":" + str(seconds)
    return final