

class UnsupportedFiletypeError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str(self):
        return str(self.message)
        

class InvalidTagValueError(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str(self):
        if self.message:
            return str("Invalid Tag Value: " + self.message)
        else:
            return "Invalid Tag Value"
            
            
class NoMusicBrainzError(Exception):
    def __init__(self, message=None):
        self.message = message
        
    def __str(self):
        m = "No MusicBrainz object"
        
        if self.message:
            m = m + ": " + self.message
            
        return str(m)
    
class NoDiscogsError(Exception):
    def __init__(self, message=None):
        self.message = message
        
    def __str(self):
        m = "No Discogs object"
        
        if self.message:
            m = m + ": " + self.message
        
        return str(m)