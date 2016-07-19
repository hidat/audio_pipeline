import os
import os.path as path
from audio_pipeline import Constants
from audio_pipeline.file_walker import ProcessLog
import abc

class Serializer(abc.ABC):

    def __init__(self, output_dir):
        """
        Serialize audio file metadata from MusicBrainz with the specified format
        
        :param output_dir: Directory to write serialized metadata to.
        """
        self.track_meta_dir = path.join(output_dir, 'track_meta')
        if not path.exists(self.track_meta_dir):
            os.makedirs(self.track_meta_dir)
        print("Track meta: ", self.track_meta_dir)
        
        if Constants.batch_constants.artist_gen:
            self.artist_meta_dir = path.join(output_dir, 'artist_meta')
            if not path.exists(self.artist_meta_dir):
                os.makedirs(self.artist_meta_dir)
            print("Artist meta: ", self.artist_meta_dir)
        
        self.release_meta_dir = path.join(output_dir, 'release_meta')
        if not path.exists(self.release_meta_dir):
            os.makedirs(self.release_meta_dir)
        print("Release meta: ", self.release_meta_dir)
        
        log_dir = path.join(output_dir, 'session_logs')
        if not path.exists(log_dir):
            os.makedirs(log_dir)
        self.logs = ProcessLog.ProcessLog(log_dir, release=True, label=True)
        print("Logs: ", self.logs.log_dir)

    @abc.abstractmethod
    def save_track(self, release, track):
        """
        Serialize track metadata to file
        
        :param release: Processed release metadata
        :pram track: Processed track metadata
        """
        pass
        
    @abc.abstractmethod
    def save_release(self, release):
        """
        Serialize release metadata to file
        
        :param release: Release metadata
        """
        pass
        
    @abc.abstractmethod
    def save_artist(self, artist, members):
        """
        Serialize artist metadata to file - if artist is a group with members,
        the metadata of all artist members will also be serialized to file.
        
        :param artist: 'Main' artist metadata
        :param members: Metadata of artist members
        """
        pass