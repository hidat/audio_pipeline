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

    def __init__(self, item_code):
        """
        Holds release metadata
        """
        
        self.item_code = item_code
        
        self.release_id = ""
        self.disc_count = None
        self.title = ""
        self.release_group_id = ""
        self.first_release_date = ""
        self.tags = []
        self.format = []
        self.artist_credit = {}
        self.disambiguation = ""
        self.labels = []
        self.date = ""
        self.country = ""
        self.barcode = ""
        self.asin = ""
        self.packaging = ""
        self.distribution_category = ""
                

class Track():
    
    def __init__(self, item_code):
        """
        Holds track metadata
        """
        self.disc_num = None
        self.track_num = None
        self.disc_count = None
        self.track_count = None

        self.release_id = ""
        self.artist_credit = []
        self.recording_id = ""
        self.track_id = ""
        self.title = ""
        self.length = None
        self.secondary_category = ""
        self.artist_dist_rule =""
        self.various_artist_dist_rule = ""
        self.item_code = item_code
        self.isrc_list = []
        self.secondary_category = ""
        self.artist_dist_rule = ""
        self.various_artist_dist_rule = ""
        self.obscenity = ""
        self.primary_genre = ""

        
class Artist():
    
    def __init__(self, item_code)
        """
        Holds artist metadata
        """
        
        self.item_code = item_code
