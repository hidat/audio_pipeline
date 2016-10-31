from audio_pipeline.util import MBInfo
import os.path as path


class Hitters:
    artist = "(Various Artists) - "
    source = "Hitters"


class BatchConstants:

    input_directory = ""
    output_directory = ""

    def __init__(self, args=None):
        self.artist_gen = True

        self.input_directory = ''
        self.output_directory = ''

        self.meta_only = False
        self.delete = False

        self.mb = None

        self.gen_item_code = None

        self.set(None)
        
    def set(self, args):
        """
        Set the batch constants

        :param args: Batch constants from the command line
        :return:
        """
        try:
            if not self.mb:
                self.mb = MBInfo.MBInfo()
        except AttributeError:
            self.mb = MBInfo.MBInfo()
            
        if args:
            if path.exists(args.input_directory):
                self.input_directory = args.input_directory
            self.output_directory = args.output_directory

            if args.no_artist:
                self.artist_gen = not args.no_artist

            if args.gen_item_code:
                self.gen_item_code = args.gen_item_code
            if args.generate:
                self.meta_only = args.generate
            if args.delete:
                self.delete = args.delete

            BatchConstants.input_directory = args.input_directory
            BatchConstants.output_directory = args.output_directory

            if args.mbhost:
                self.mb.set_mbhost(args.mbhost)
            if args.backup:
                self.mb.set_remote(args.backup)

                
class Content:

    glossary_type = "content"
    
    def __init__(self, item_code, id="", title=""):
        """
        Hold the metadata for a piece of content
        """
        
        self.item_code = item_code
        
        self.id = id
        self.title = title
                

class Release(Content):

    release_group_url = 'http://musicbrainz.org/release-group/'

    content_type = 'Release'
    glossary_type = content_type
    
    def __init__(self, item_code, id="", title=""):
        """
        Holds release metadata
        """
        super().__init__(item_code, id, title)
        
        self.release_group_id = ""
        self.disc_count = None
        self.first_released = ""
        self.tags = []
        self.format = []
        self.disambiguation = ""
        self.labels = []
        self.media = []
        self.release_type = ""
        
        self.artist_ids = []
        self.artist = ''
        self.artist_sort_names = []
        
        self.date = ""
        self.country = ""
        self.barcode = ""
        self.asin = ""
        self.packaging = ""
        self.distribution_category = ""
        self.secondary_genre = ""
        
        self.glossary_title = ''

class Disc:

    def __init__(self, disc_num, tracks):
        self.disc_num = disc_num
        self.tracks = tracks


class Track(Content):
    
    content_type = "music library track"
    
    def __init__(self, item_code="", id="", title=""):
        """
        Holds track metadata
        """
        super().__init__(item_code, id, title)

        self.disc_num = None
        self.track_num = None
        self.disc_count = None
        self.track_count = None

        self.release_id = ""
        self.recording_id = ""
        self.length = None
        self.secondary_category = None
        self.isrc_list = []
        self.artist_dist_rule = ""
        self.various_artist_dist_rule = ""
        self.obscenity = ""
        self.primary_genre = ""
        self.type = ""
        
        self.radio_edit = False
        self.artists = []
        self.artist_credit = ''
        self.artist_phrase = ''
        
        self.anchor_status = None
        
    def set_type(self):
        if self.item_code and (self.item_code != self.id):
            self.type = "track with filewalker mbid"
        else:
            self.type = "track"
        
        
class Artist(Content):

    content_type = 'Artist'
    glossary_type = content_type
    
    def __init__(self, item_code, id="", title=""):
        """
        Holds artist metadata
        """
        super().__init__(item_code, id, title)
        
        self.disambiguation = ''
        self.name = ''
        self.sort_name = ''
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
        

class Label(Content):

    content_type = 'label'
    glossary_type = content_type
    
    def __init__(self, item_code, id="", title=""):
    
        super().__init__(item_code, id, title)
    
        self.catalog_num = ""

        
class NameId():

    def __init__(self, name='', id=''):
        """
        Holds information about something that has a 'name'
        and an 'id'
        """
        self.name = name
        self.id = id


class Genre:
    def __init__(self, main, aliases):
        self.main = main
        self.aliases = set(aliases)


class Genres:
    set_secondary = {"Local": "Rock/Pop"}

    genres = {Genre("Recent Acquisitions", ["recent acquisitions", "acq"]),
              Genre("Electronic", ["ele", "electronic"]), Genre("Hip Hop", ["hip", "hip hop"]),
              Genre("Jazz", ["jaz", "jazz"]), Genre("Live on KEXP", ["liv", "live on kexp"]),
              Genre("Local", ["local"]), Genre("Reggae", ["reggae", "reg"]),
              Genre("Rock/Pop", ["rock", "pop", "rock/pop", "roc"]), Genre("Roots", ["roots", "roo"]),
              Genre("Rotation", ["rotation", "rot"]), Genre("Shows Around Town", ["shows around town", "sho"]),
              Genre("Soundtracks", ["soundtracks", "sou"]), Genre("World", ["world", "wor"]),
              Genre("", ["", " "])}

    @classmethod
    def get(cls, val):
        val = val.casefold()
        for g in cls.genres:
            if val in g.aliases:
                return g.main

