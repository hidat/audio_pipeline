import audio_pipeline.file_walker.Resources as default_resources


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
        self.category = None
        self.source = None
        self.rotation = None

        self.gen_item_code = False
        self.anchor = False

        self.set(args)

    def set(self, args):
        super().set(args)
        self.category = self.category_options[args.category] if args.category != None else ""
        self.rotation = self.rotation_options[args.rotation] if args.rotation != None else ""
        self.source = self.source_options[args.source] if args.source != None else ""

        self.gen_item_code = args.gen_item_code
        self.anchor = args.anchor


class Release():

    glossary_type = 'Release'

    def __init__(self, item_code):
        """
        Holds release metadata
        """

        self.item_code = item_code

        self.id = ""
        self.title = ""
        self.release_group_id = ""
        self.disc_count = None
        self.first_released = ""
        self.tags = []
        self.format = []
        self.disambiguation = ""
        self.labels = []

        self.artist_ids = []
        self.artist = ''
        self.artist_sort_names = []

        self.date = ""
        self.country = ""
        self.barcode = ""
        self.asin = ""
        self.packaging = ""
        self.distribution_category = ""

        self.glossary_title = ''


class Track():

    content_type = "music library track"

    def __init__(self, item_code):
        """
        Holds track metadata
        """
        self.disc_num = None
        self.track_num = None
        self.disc_count = None
        self.track_count = None

        self.release_id = ""
        self.recording_id = ""
        self.id = ""
        self.title = ""
        self.length = None
        self.secondary_category = None
        self.item_code = item_code
        self.isrc_list = []
        self.artist_dist_rule = ""
        self.various_artist_dist_rule = ""
        self.obscenity = ""
        self.primary_genre = ""
        self.type = ""

        self.radio_edit = False
        self.artists = []
        self.artist_credit = ''

        self.anchor_status = None


class Artist():

    glossary_type = 'Artist'

    def __init__(self, item_code):
        """
        Holds artist metadata
        """

        self.item_code = item_code
        self.disambiguation = ''
        self.title = ''
        self.name = ''
        self.sort_name = ''
        self.id = ''
        self.annotation = ''
        self.type = ''

        self.begin_area = NameId('', '')
        self.end_area = NameId('', '')
        self.begin_date = ''
        self.end_date = ''
        self.ended = None

        self.country = NameId('', '')

        self.alias_list = []
        self.ipi_list = []
        self.isni_list = []
        self.url_relation_list = []

        self.group_members = []


class NameId:

    def __init__(self, name='', id=''):
        """
        Holds information about something that has a 'name'
        and an 'id'
        """
        self.name = name
        self.id = id

class Label(NameId):

    def __init__(self, name='', id='', catalog_num=''):
        super().__init__(name, id)
        self.catalog_num = catalog_num