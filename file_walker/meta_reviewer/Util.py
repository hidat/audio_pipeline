file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis", "ERROR_EXT": "ERROR_EXT"}

release_mapping = {"name": "Album Name", "album_artist": "Album Artist", "disc_num": "Disc"}
track_mapping = {"name": "Title", "artist": "Artist", "track_num": "Track Number", "length": "Length",
                 "KEXPFCCOBSCENITYRATING": "KEXPFCCOBSCENITYRATING"}

# List of the names of track and release data elements, in the order I want them displayed
track_categories = ["track_num", "name", "artist", "length", "KEXPFCCOBSCENITYRATING"]
release_categories = ["name", "album_artist", "disc_num"]


kexp_tags = {"obscenity": "KEXPFCCOBSCENITYRATING", "genre": "KEXPPRIMARYGENRE"}
kexp_values = {"y": "YELLOW DOT", "r": "RED DOT"}

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

