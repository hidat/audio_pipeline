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

class Obscenity:
    red = "RED DOT"
    yellow = "YELLOW DOT"
    clean = "CLEAN EDIT"