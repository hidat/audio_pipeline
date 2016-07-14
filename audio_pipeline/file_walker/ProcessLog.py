import datetime
import os


class ProcessLog:

    type_index = 0
    id_index = 1
    name_index = 2

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
        
        
    ######################
    #   Release log has the format
    #       <type>  <item_code> <name>  <release_artist>    <glossary_title>
    ######################
        
    def log_release(self, release):
        log_items = self.log_list(release)
        if log_items:
            log_items.insert(self.id_index + 1, release.artist)
            log_items.append(release.glossary_title)
            self.save_log(self.log_file, log_items)
            if self.release_log:
                self.save_log(self.release_log, log_items)
        
    
    ####################
    #   Track, Artist, Label all have format
    #           <type>  <item_code>  <name>
    ####################
    
    
    def log_track(self, track):
        log_items = self.log_list(track)
        if log_items:
            self.save_log(self.log_file, log_items)
    
    def log_artist(self, artist, group_members = []):
        logs = list()
        log = self.log_list(artist)
        if log:
            logs.append(log)
        for member in group_members:
            log = self.log_list(member)
            if log:
                logs.append(log)
        self.save_log(self.log_file, logs)
                    
    def log_label(self, label):
        log_items = self.log_list(label)
        if log_items:
            self.save_log(self.log_file, log_items)
            if self.label_log:
                self.save_log(self.label_log, log_items)
            
    def log_fail(self, glossary):
        log_items = self.log_list(glossary)
        self.save_log(self.failure_log, log_items)
            
    def log_list(self, content):
        """
        Returns a list of the format
            <content.type>  <content.item_code> <content.name>
        """
        if content.item_code not in self.glossaries:
            log_items = [str(content.content_type), str(content.item_code), str(content.title)]
            return log_items
        return None
            
    def save_log(self, log_file, log_items):
        if len(log_items) > 0:
            with open(log_file, 'ab') as file:
                if isinstance(log_items[0], str):
                    log = "\t".join(log_items)
                    log += "\r\n"
                    file.write(log.encode('UTF-8'))
                else:
                    for log in log_items:
                        log = "\t".join(log)
                        log += "\r\n"
                        file.write(log.encode('UTF-8'))
