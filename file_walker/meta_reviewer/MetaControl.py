import MetaModel
import MetaView
import sys
from Util import *


class MetaController:

    def __init__(self, root_dir):
        self.meta_model = MetaModel.process_directory(root_dir)
        self.root_dir = root_dir

        if self.meta_model.has_next():
            releases, tracks = self.meta_model.get_meta()
            for directory, release_info in releases.items():
                self.frame = MetaView.MetaFrame(self.process_input, release_info, tracks)
                self.frame.mainloop()

    def process_input(self, event):
        contents = self.frame.input_value.get().split()
        content_length = len(contents)
        print(contents)
        if content_length == 2:
            try:
                track_num = int(contents[0])
                value = contents[1].casefold()
                if track_num not in self.frame.current_tracks.keys():\
                   print("Invalid Track Number")
                else:
                    file_name = self.frame.current_tracks[track_num]            
                if value == "y" or value == "yellow" or value == "yellow dot":
                    new_meta = {kexp_tags["obscenity"]: kexp_values["y"]}
                    self.meta_model.update_metadata(file_name, new_meta)
                    self.frame.yellow(file_name)
                    self.frame.clear_input()
                elif value == "r" or value == "red" or value == "red dot":
                    new_meta = {kexp_tags["obscenity"]: kexp_values["r"]}
                    self.meta_model.update_metadata(file_name, new_meta)
                    self.frame.red(file_name)
                    self.frame.clear_input()
                else:
                    print("Invalid Input")
            except ValueError: # find out what the tried-to-turn-non-integer-into-int exception is
                print("Invalid Input")
        if content_length == 1:
            value = contents[0].casefold()
            if value == "done":
                # move to next album
                self.next_album()

    def next_album(self):
        self.frame.quit()
        if self.meta_model.has_next():
            releases, tracks = self.meta_model.get_meta()
            for directory, release_info in releases.items():
                self.frame = MetaView.MetaFrame(release_info, tracks)
                self.frame.mainloop()
        else:
            self.frame.quit()
        
                
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
