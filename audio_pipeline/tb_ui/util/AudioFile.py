from ... import util
from ..view import Settings
from ..util import Resources

class UnsupportedFiletypeError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str(self):
        return str(self.message)

class AudioFile(util.AudioFile.AudioFile):

    release_style = {'anchor': 'nw', 'bg': Settings.bg_color, 'foreground': Settings.text_color, 
                                 'font': Settings.standard, 'activeforeground': Settings.active_fg,
                                 'activebackground': Settings.active_bg, 'justify': 'left'}
    name_style = {'anchor': 'nw', 'justify': 'left', 'background': Settings.bg_color,
                  'foreground': Settings.text_color, 'font': Settings.heading}

    def __init__(self, file_name, picard, mb):
        """
        An AudioFile object that has all information about audiofile tags as a standard AudioFile,
        but also encodes UI formatting inforation for each tags.
        super().__init__()
        
        """
        try: 
            super().__init__(file_name)
        except util.AudioFile.UnsupportedFiletypeError:
            raise UnsupportedFiletypeError(file_name)
            
        self.track_style = self.release_style.copy()
        self.track_style['fg'] = Settings.get_text_color(self)
        
        self.mbid.style = self.style(30, False)
        self.album.style = self.style(30, False)
        self.album_artist.style = self.style(25, False)
        self.release_date.style = self.style(15, False)
        self.disc_num.style = self.style(10, False)
        self.label.style = self.style(20, False)

        self.title.style = self.style(30, True)
        self.artist.style = self.style(25, True)
        self.track_num.style = self.style(5, True)
        self.length.style = self.style(10, True)
        
        if self.kexp:
            self.kexp.obscenity.style = self.style(20, True)
            self.kexp.primary_genre.style = self.style(20, True)

        self.picard = picard
        self.mb = mb

        self.dest_file = self.move_file()


    def move_file(self):
        if Resources.has_mbid(self):
            self.dest_file = self.mb
        else:
            self.dest_file = self.picard

        return self.dest_file

    def save_mbid(self, mbid):
        super().save_mbid(mbid)

        self.dest_file = self.move_file()

    def save(self):
        super().save()

        self.dest_file = self.move_file()
                    
    def style(self, width, track):
        if track:
            configuration = self.track_style.copy()
        else:
            configuration = self.release_style.copy()
        configuration['width'] = width
        configuration['wraplength'] = 8 * width
        return configuration
        