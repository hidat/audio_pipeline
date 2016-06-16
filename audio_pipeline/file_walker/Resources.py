import os
import configparser
from .. import util

audiofile_options = {"kexp": util.KEXPAudioFile.KEXPAudioFile}

config_defaults = {"LocalServer": "",
                   "RemoteServer": 'musicbrainz.org',
                   "Delete": "no",
                   "Generate": "no"}


class Hitters():
    artist = "(Various Artists) - "
    source = "Hitters"


class BatchConstants():
    obscenity = None
    category = None
    source = None
    rotation = None
    
    input_directory = ''
    output_directory = ''
    
    gen_item_code = False
    generate = False
    delete = False
    
    remote_server = None
    local_server = None
    
    initial_server = None
    backup_server = None

    @classmethod
    def config(cls, config_file, args):
    
        # dict of passed choices -> what we want for category, source, and rotation
        options = {"acq": "Recent Acquisitions", "recent acquisitions": "Recent Acquisitions", "electronic": "Electronic",
                   "ele": "Electronic", "exp": "Experimental", "experimental": "Experimental", "hip": "Hip Hop",
                   "hip hop": "Hip Hop", "jaz": "Jazz", "jazz": "Jazz", "liv": "Live on KEXP", "live on kexp": "Live on Kexp",
                   "loc": "Local", "local": "Local", "reg": "Reggae", "reggae": "Reggae", "roc": "Rock/Pop", "rock": "Rock/Pop",
                   "pop": "Rock/Pop", "rock/pop": "Rock/Pop", "roo": "Roots", "roots": "Roots",
                   "rot": "Rotation", "rotation": "Rotation", "sho": "Shows Around Town", "shows around town": "Shows Around Town",
                   "sou": "Soundtracks", "soundtracks": "Soundtracks", "wor": "World", "world": "World",
                   "cd library": "CD Library", "melly": "Melly", "hitters": "Hitters",
                   "heavy": "Heavy", "library": "Library", "light": "Light", "medium": "Medium", "r/n": "R/N"}

        config = configparser.ConfigParser(allow_no_value=True)
        
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # create / write new config file
            config['DEFAULT'] = config_defaults
        
        if "USER" not in config:
            config["USER"] = {}
         
        if args.local:
            config["USER"]["LocalServer"] = args.local
        if args.remote:
            config["USER"]["RemoteServer"] = args.remote
            
        # write configuration
        with open(config_file, 'w+') as c_file:
            config.write(c_file)
            
        # set batch constants from config file
        settings = config["USER"]
        cls.local_server = settings.get("LocalServer")
        cls.remote_server = settings.get("RemoteServer")
        cls.generate = settings.getboolean("Generate")
        cls.delete = settings.getboolean("Delete")
        
        # set AudioFile from config file
        util.AudioFile.AudioFileFactory.audiofile = audiofile_options[settings.get("AudioFile")] if settings.get("AudioFile") in audiofile_options else util.AudioFile.BaseAudioFile
        
        # set batch constants from batch arguments
        cls.category = options[args.category] if args.category != None else ""
        cls.rotation = options[args.rotation] if args.rotation != None else ""
        cls.source = options[args.source] if args.source != None else ""
        
        cls.gen_item_code = args.gen_item_code
        cls.generate = args.generate
        cls.delete = args.delete
        
        cls.input_directory = args.input_directory
        cls.output_directory = args.output_directory
        
        # set initial / backup server
        order = args.mb_server
        first = order[0]
        second = order[1] if len(order) > 1 else None

        if cls.local_server:
            if first == 'l':
                cls.initial_server = cls.local_server
            else:
                cls.initial_server = cls.remote_server

            if second:
                if second == 'l':
                    cls.backup_server = cls.local_server
                else:
                    cls.backup_server = cls.remote_server
        elif cls.remote_server:
            cls.initial_server = cls.remote_server
            cls.backup_server = cls.remote_server
            
        # set which AudioFile we use
        

                
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
        

class NameId():

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