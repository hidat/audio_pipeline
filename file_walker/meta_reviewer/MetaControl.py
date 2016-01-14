import MetaModel
import MetaView
import sys
from Util import *
import re


class MetaController:

    def __init__(self, root_dir):
    """
    MetaController is in charge of sending commands to the view and getting information from the model.
    
    """
        self.meta_model = MetaModel.process_directory(root_dir)
        self.root_dir = root_dir

        self.base_frame = MetaView.AppFrame(self.process_input)
        self.base_frame.allow_input(self.process_input)
        
        if self.meta_model.has_next():
            releases, tracks = self.meta_model.get_next_meta()
            for directory, release_info in releases.items():
                self.base_frame.display_meta(release_info, tracks)
                self.base_frame.mainloop()

                
    def process_input(self, event):
    """
    Process the user-inputted metadata
    """
        contents = self.base_frame.get_input().split()
        content_length = len(contents)
        if content_length == 2:
            try:
                track_num = int(contents[0])
                value = contents[1].casefold()
                self.new_meta_input(track_num, value)
            except ValueError: # find out what the tried-to-turn-non-integer-into-int exception is
                print("Invalid Input")
        if content_length == 1:
            value = contents[0].casefold()
            self.change_displayed_album(value)
            
            
    def new_meta_input(self, track_num, value):
    """
    When we have input we've determined is (probably) metadata,
    add it to the metadata of the specified track
    """
        if track_num not in self.base_frame.current_tracks.keys():
        
           print("Invalid Track Number")
        else:
            file_name = self.frame.current_tracks[track_num]            
        if value == "y" or value == "yellow" or value == "yellow dot":
            new_meta = {kexp_tags["obscenity"]: kexp_values["y"]}
        elif value == "r" or value == "red" or value == "red dot":
            new_meta = {kexp_tags["obscenity"]: kexp_values["r"]}
        else:
            print("Invalid Input")
            
        if new_meta:
            self.meta_model.update_metadata(file_name, new_meta)
            self.frame.update_track(file_name, new_meta)
            self.frame.clear_input()
            
            
    def change_displayed_album(self, command):
    """
    Changes the album metadata on screen to the previous or next in the directory list,
    depending on the command that is passed in.
    """
        if command == "done" or command == "next":
            if self.meta_model.has_next():
                releases, tracks = self.meta_model.get_next_meta()
                self.next_album(releases, tracks)
            else:
                self.last_album()
        elif command == "prev" or command == "previous" or command == "last":
            if self.meta_model.has_prev():
                releases, tracks = self.meta_model.get_previous_meta()
                self.next_album(releases, tracks)
            else:
                self.last_album()

                
    def next_album(self, releases, tracks):
        for directory, release_info in releases.items():
            self.base_frame.display_meta(release_info, tracks)
            
            
    def last_album(self):
        self.base_frame.complete_button()
                
                
def main():
    if len(sys.argv) < 2:
        print('asdkj')
        exit(2)
        
    directory = sys.argv[1]
    controller = MetaController(directory)

main()
