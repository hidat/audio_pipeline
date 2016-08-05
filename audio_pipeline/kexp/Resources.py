import audio_pipeline.util.Resources as default_resources


class Hitters:
    artist = "(Various Artists) - "
    source = "Hitters"


class BatchConstants(default_resources.BatchConstants):
    category_options = {"acq": "Recent Acquisitions", "recent acquisitions": "Recent Acquisitions", "electronic": "Electronic",
               "ele": "Electronic", "exp": "Experimental", "experimental": "Experimental", "hip": "Hip Hop",
               "hip hop": "Hip Hop", "jaz": "Jazz", "jazz": "Jazz", "liv": "Live on KEXP", "live on kexp": "Live on Kexp",
               "loc": "Local", "local": "Local", "reg": "Reggae", "reggae": "Reggae", "roc": "Rock/Pop", "rock": "Rock/Pop",
               "pop": "Rock/Pop", "rock/pop": "Rock/Pop", "roo": "Roots", "roots": "Roots",
               "rot": "Rotation", "rotation": "Rotation", "sho": "Shows Around Town", "shows around town": "Shows Around Town",
               "sou": "Soundtracks", "soundtracks": "Soundtracks", "wor": "World", "world": "World"}

    source_options = {"cd library": "CD Library", "melly": "Melly", "hitters": "Hitters"}

    rotation_options = {"heavy": "Heavy", "library": "Library", "light": "Light", "medium": "Medium", "r/n": "R/N"}

    def __init__(self, args):
        super().__init__(args)

        self.obscenity = None
        self.category = ""
        self.source = ""
        self.rotation = ""

        self.gen_item_code = False
        self.anchor = False

    def set(self, args):
        super().set(args)
        if args:
            if args.category is not None:
                self.category = self.category_options[args.category]
            if args.rotation is not None:
                self.rotation = self.rotation_options[args.rotation]
            if args.source is not None:
                self.source = self.source_options[args.source]

            if args.anchor:
                self.anchor = args.anchor


class Release(default_resources.Release):

    glossary_type = 'Release'

    def __init__(self, item_code):
        """
        Holds release metadata
        """
        super().__init__(item_code)
        
        self.distribution_category = ""

        self.glossary_title = ''


class Track(default_resources.Track):

    content_type = "music library track"

    def __init__(self, item_code=""):
        """
        Holds track metadata
        """
        super().__init__(item_code)
        self.secondary_category = None
        self.artist_dist_rule = ""
        self.various_artist_dist_rule = ""
        self.obscenity = ""
        self.primary_genre = ""
        self.type = ""

        self.radio_edit = False

        self.anchor_status = None


class Artist(default_resources.Artist):

    glossary_type = 'Artist'

    def __init__(self, item_code):
        """
        Holds artist metadata
        """
        super().__init__(item_code)
        self.type = ''


class NameId(default_resources.NameId):

    def __init__(self, name='', id=''):
        """
        Holds information about something that has a 'name'
        and an 'id'
        """
        super().__init__(name, id)
        
        
class Label(default_resources.Label):

    def __init__(self, name='', id='', catalog_num=''):
        super().__init__(name, id)
        self.catalog_num = catalog_num
        