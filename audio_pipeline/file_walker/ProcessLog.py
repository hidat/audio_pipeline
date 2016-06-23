import datetime
import os


class ProcessLog:

    def __init__(self, output_dir, release=True, label=True):
        """
        Writes logs for releases, tracks, labels, and artists.
        
        :param output_dir: Name of log output directory
        :param release: True to generate a file of only release logs, False otherwise.
        :param labek: True to generate a file of only label logs, False otherwise.
        """
        self.log_dir = output_dir
        self.release_log = None
        self.label_log = None
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
        # set up log file:
        date_time = datetime.datetime
        now = date_time.now()
        
        self.log_file = os.path.join(self.log_dir, now.strftime("filewalker_log_%d-%m-%y-%H%M%S%f.txt"))
        
        if release:
            self.release_log = os.path.join(self.log_dir, now.strftime("release_log_%d-%m-%y-%H%M%S%f.txt"))
        
        if label:
            self.label_log = os.path.join(self.log_dir, now.strftime("label_log_%d-%m-%y-%H%M%S%f.txt"))

        # to prevent duplicates, we'll keep a set of release, artist, track, and label item codes
        self.releases = set([])
        self.tracks = set([])
        self.artists = set([])
        self.labels = set([])
        
    def log_release(self, release):
        if release.item_code not in self.releases:
            log_text = str(release.glossary_type) + "\t" + str(release.item_code) + '\t' + str(release.title) + '\r\n'
            self.save_log(self.log_file, log_text)
            if self.release_log:
                self.save_log(self.release_log, log_text)
        
    def log_track(self, track):
        if track.item_code not in self.tracks:
            log_text = str(track.type) + '\t' + str(track.item_code) + '\t' + str(track.title) + '\r\n'
            self.save_log(self.log_file, log_text)
    
    def log_artist(self, artist, group_members = []):
        if artist.item_code not in self.artists:
            log_text = str(artist.glossary_type) + "\t" + str(artist.item_code) + '\t' + str(artist.title) + '\r\n'
            self.save_log(self.log_file, log_text)
        with open(self.log_file, 'ab') as file:
            for member in group_members:
                if member.item_code not in self.artists:
                    log_text = str(member.glossary_type) + "\t" + str(member.item_code) + '\t' + str(member.title) + '\r\n'
                    file.write(log_text.encode('UTF-8'))
                    
    def log_label(self, label):
        if label.id not in self.labels:
            log_text = 'label\t' + str(label.id) + '\t' + str(label.name) + '\r\n'
            self.save_log(self.log_file, log_text)
            if self.label_log:
                self.save_log(self.label_log, log_text)
            
    def save_log(self, log_file, log_text):
        with open(log_file, 'ab') as file:
            file.write(log_text.encode('UTF-8'))
        