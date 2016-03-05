import datetime

class ProcessLog:

    
    def __init__(self, output_dir, dir_name):
        self.log_dir = os.path.join(output_dir, dir_name)
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
        # set up log file:
        date_time = datetime.datetime
        now = date_time.now()
        
        self.log_file = os.path.join(self.log_dir, now.strftime("filewalker_log_%d-%m-%y-%H%M%S%f.txt")
        
        # to prevent duplicates, we'll keep a set of release, artist, track, and label item codes
        self.releases = set([])
        self.tracks = set([])
        self.artists = set([])
        self.labels = set([])

        
    def log_release(self, release):
        if release.item_code not in self.releases:
            log_text = str(release.glossary_type) + str(release.item_code) + '\t' + str(release.release_title) + '\r\n'
            with open(self.log_file, 'ab') as file:
                file.write(log_text.encode('UTF-8'))
        
    def log_track(self, track):
        if track.item_code not in self.tracks:
            log_text = str(track.type) + '\t' + str(track.item_code) + '\t' + str(track.title) + '\r\n'
            with open(self.log_file, 'ab') as file:
                file.write(log_text.encode('UTF-8'))
    
    def log_artist(self, artist):
        if artist.item_code not in artists:
            log_text = str(artist.glossary_type) + str(artist.item_code) + '\t' + str(artist.title) + '\r\n'
            with open(self.log_file, 'ab') as file:
                file.write(log_text.encode('UTF-8'))
            
    def log_label(self, label):
        if label.id not in labels:
            log_text = 'label\t' + str(label.id) + '\t' + str(label.name) + '\r\n'
            with open(self.log_file, 'ab') as file:
                file.write(log_text.encode('UTF-8'))
        