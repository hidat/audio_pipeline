import datetime
import os


class ProcessLog:

    def __init__(self, output_dir, release=True, label=True):
        """
        Writes logs for releases, tracks, labels, and artists.
        
        [Currently, logging is performed by the serializer]
        
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
        self.failure_log = os.path.join(self.log_dir, now.strftime("failure_log_%d-%m-%y-%H%M%S%f.txt"))

        if release:
            self.release_log = os.path.join(self.log_dir, now.strftime("release_log_%d-%m-%y-%H%M%S%f.txt"))
        
        if label:
            self.label_log = os.path.join(self.log_dir, now.strftime("label_log_%d-%m-%y-%H%M%S%f.txt"))

        # to prevent duplicates, we'll keep a set of release, artist, track, and label item codes
        self.glossaries = set([])
        
        
    def log_release(self, release):
        log_text = self.log_string(release)
        if log_text:
            log_text = log_text.strip() + "\t" + release.glossary_title + "\r\n"
            self.save_log(self.log_file, log_text)
            if self.release_log:
                self.save_log(self.release_log, log_text)
        
    def log_track(self, track):
        log_text = self.log_string(track)
        if log_text:
            self.save_log(self.log_file, log_text)
    
    def log_artist(self, artist, group_members = []):
        log_text = self.log_string(artist)
        if log_text:
            self.save_log(self.log_file, log_text)
        with open(self.log_file, 'ab') as file:
            for member in group_members:
                log_text = self.log_string(artist)
                if log_text:
                    self.save_log(self.log_file, log_text)
                    file.write(log_text.encode('UTF-8'))
                    
    def log_label(self, label):
        log_text = self.log_string(label)
        if log_text:
            self.save_log(self.log_file, log_text)
            if self.label_log:
                self.save_log(self.label_log, log_text)
            
    def log_fail(self, glossary):
        log_text = log_string(glossary)
        self.save_log(self.failure_log, log_text)
            
    def log_string(self, glossary):
        if glossary.item_code not in self.glossaries:
            log_text = str(glossary.glossary_type) + "\t" + str(glossary.item_code) + "\t" + str(glossary.title) + "\r\n"
            return log_text
        return None
            
    def save_log(self, log_file, log_text):
        with open(log_file, 'ab') as file:
            file.write(log_text.encode('UTF-8'))
        