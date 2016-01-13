import MetaModel
import MetaView
import sys
from Util import *
import re


class MetaController:

    def __init__(self, root_dir):
        self.meta_model = MetaModel.process_directory(root_dir)
        self.root_dir = root_dir

        self.base_frame = MetaView.AppFrame()
        
        if self.meta_model.has_next():
            releases, tracks = self.meta_model.get_next_meta()
            for directory, release_info in releases.items():
                self.frame = MetaView.MetaFrame(self.process_input, release_info, tracks, master=self.base_frame)
                self.frame.mainloop()        

    def process_input(self, event):
        contents = self.frame.input_value.get().split()
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
        # if we had an input that we've determined is new metadata,
        # add it to the metadata of the specified track
        if track_num not in self.frame.current_tracks.keys():\
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
        # change the album data we're seeing
        if command == "done" or command == "next":
            if self.meta_model.has_next():
                releases, tracks = self.meta_model.get_next_meta()
                self.next_album(releases, tracks)
            else:
                self.frame.really_quit()
        elif command == "prev" or command == "previous" or command == "last":
            if self.meta_model.has_prev():
                releases, tracks = self.meta_model.get_previous_meta()
                self.next_album(releases, tracks)
            else:
                self.frame.really_quit()

    def next_album(self, releases, tracks):
        self.frame.quit()
        for directory, release_info in releases.items():
            self.frame = MetaView.MetaFrame(self.process_input, release_info, tracks, master=self.base_frame)
            self.frame.mainloop()        
                
def main():
    if len(sys.argv) < 2:
        print('asdkj')
        exit(2)
        
    directory = sys.argv[1]
    controller = MetaController(directory)
    
    # while meta_model.has_next():
        # releases, tracks = meta_model.get_meta()
        # for dir, release_info in releases.items():
            # MetaView.display_metadata(release_info, tracks)

main()
