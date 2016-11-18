from ..util import Resources
import os


class Rule:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.forbidden = ["\\", "/", ":", "?", "*", "[", "]", ">", "<", "|", "\""]

    def clean_filename(self, name):
        for f in self.forbidden:
            name = name.replace(f, "")
        return name


class FileUnderRule(Rule):

    def get_dest(self, audiofile):
        if audiofile.file_under.value:
            # we're going to ignore casing
            layer_one = audiofile.file_under.value[:1].upper()
            layer_two = os.path.join(layer_one, audiofile.file_under.value.upper())
            directory = str(audiofile.album_artist) + " - " + self.clean_filename(str(audiofile.album))
            dest = os.path.join(layer_two, directory)
            return dest


class KEXPDestinationDirectoryRule(Rule):

    def __init__(self, dest_dir):
        super().__init__(dest_dir)
        self.picard_dir = Resources.picard_directory
        self.mbid_dir = Resources.mbid_directory
        
    def get_dest(self, audiofile):
        # get the name of the release directory
        directory = os.path.split(os.path.dirname(audiofile.file_name))[1]
        
        if Resources.has_mbid(audiofile):
            dest = os.path.join(self.mbid_dir, directory)
        else:
            dest = os.path.join(self.picard_dir, directory)
            
        return dest