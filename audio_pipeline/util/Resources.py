import yaml
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

        self.remote_server = None
        self.local_server = None

        self.initial_server = None
        self.backup_server = None

        self.gen_item_code = None

        if args:
            self.set(args)
        
    def set(self, args):
        """
        Set the batch constants

        :param args: Batch constants from the command line
        :return:
        """
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
            self.local_server = args.mbhost

        # set initial / backup server
        if (args.mb_server != 'lr'):
            order = args.mb_server
            first = order[0]
            second = order[1] if len(order) > 1 else None

            if self.local_server:
                if first == 'l':
                    self.initial_server = self.local_server
                else:
                    self.initial_server = self.remote_server

                if second:
                    if second == 'l':
                        self.backup_server = self.local_server
                    else:
                        self.backup_server = self.remote_server
            elif self.remote_server:
                self.initial_server = self.remote_server
                self.backup_server = self.remote_server

                
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


class Track(Content):
    
    content_type = "music library track"
    
    def __init__(self, item_code, id="", title=""):
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
        if (self.item_code != self.id):
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
                