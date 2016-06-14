from ..util import Resources
import os


class KEXPDestinationDirectoryRule:

    def __init__(self, dest_dir):
        self.picard_dir = os.path.join(dest_dir, Resources.picard_directory)
        self.mbid_dir = os.path.join(dest_dir, Resources.mbid_directory)
        
    def get_dest(self, audiofile):
        # get the name of the release directory
        directory = os.path.split(os.path.split(audiofile.file_name)[0])[1]
        
        if Resources.has_mbid(audiofile):
            dest = os.path.join(self.mbid_dir, directory)
        else:
            dest = os.path.join(self.picard_dir, directory)
            
        if not (os.path.exists(dest)):
            os.makedirs(dest)

        return dest