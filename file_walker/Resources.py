class BatchConstants():
    obscenity = None
    category = None
    source = None
    rotation = None
    
    input_directory = ''
    output_directory = ''
    
    generate = False
    delete = False
    local_server = False
    
    mbhost = None
        
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
        
        self.artists = []
        self.artist_credit = ''
        
        
class Artist():

    glossary_type = 'Artist'
    
    def __init__(self, item_code)
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