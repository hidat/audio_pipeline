import MetaModel
import MetaView
import sys
from Util import *
import re

tracknum_acc = "track_num"
meta_acc = "meta"
command_acc = "command"

track_meta_pattern = re.compile('(?P<' + tracknum_acc + '>\d+)\s*(?P<' + meta_acc + '>.+)')
command_pattern = re.compile('(?P<' + command_acc + '>.+)')

class MetaController:

    def __init__(self, root_dir):
        """
        MetaController is in charge of sending commands to the view and getting information from the model.
        
        """
        self.meta_model = MetaModel.process_directory(root_dir)
        self.root_dir = root_dir

        self.quit_command = False
        self.base_frame = MetaView.AppFrame(self.process_input)
        self.base_frame.allow_input(self.process_input)
        
        if self.meta_model.has_next():
            releases, tracks = self.meta_model.get_next_meta()
            directory, release_info = releases.popitem()
            self.base_frame.display_meta(release_info, tracks)
            self.base_frame.mainloop()
                
                                
    def process_input(self, event):
        """
        Process the user-inputted metadata
        """
        input_string = self.base_frame.get_input()
        match = track_meta_pattern.match(input_string)
        if match:
            # we (probably) have a track metadata match (currently only RED DOT, YELLOW DOT)
            # process it accordingly
            try:
                track_num = int(match.group(tracknum_acc))
                value = match.group(meta_acc)
                self.new_meta_input(track_num, value)
            except ValueError:
                print("Invalid Input")
        else:
            command = input_string.split()[0]
            self.change_displayed_album(command)


    def new_meta_input(self, track_num, value):
        """
        When we have input we've determined is (probably) metadata,
        add it to the metadata of the specified track
        """
        yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
        red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
        new_meta = None
        
        if track_num not in self.meta_model.current_tracks.keys():
           print("Invalid Track Number")
        else:
            file_name = self.meta_model.current_tracks[track_num]
            if yellow_dot.match(value):
                new_meta = {kexp_tags["obscenity"]: kexp_values["y"]}
            elif value == "r" or value == "red" or value == "red dot":
                new_meta = {kexp_tags["obscenity"]: kexp_values["r"]}
            else:
                print("Invalid Input")      
        
        if new_meta:
            self.meta_model.update_metadata(file_name, new_meta)
            self.base_frame.update_track(file_name, new_meta)
            self.base_frame.clear_input()
            
    def change_displayed_album(self, command):
        """
        Changes the album metadata on screen to the previous or next in the directory list,
        depending on the command that is passed in.
        """
        
        # FIX THESE SO THEY ARE *SLIGHTLY* MORE SPECIFIC
        yes_pattern = re.compile("\s*y+e*.*", flags=re.I)
        no_pattern = re.compile("\s*n+o*", flags=re.I)
        prev_pattern = re.compile("\s*p(rev)?.*", flags=re.I)
        next_pattern = re.compile("\s*n(ext)?", flags=re.I)
        done_pattern = re.compile("\s*d+(one)?", flags=re.I)
        help_pattern = re.compile("\s*h(elp)?", flags=re.I)
        
        if self.quit_command:
            if yes_pattern.match(command):
                self.base_frame.quit()
            elif no_pattern.match(command):
                self.base_frame.clear_label()
                self.quit_command = False
        else:
            if next_pattern.match(command):
                if self.meta_model.has_next():
                    releases, tracks = self.meta_model.get_next_meta()
                    self.next_album(releases, tracks)
                else:
                    self.last_album()
            elif prev_pattern.match(command):
                if self.meta_model.has_prev():
                    releases, tracks = self.meta_model.get_previous_meta()
                    self.next_album(releases, tracks)
                else:
                    self.last_album()
            elif done_pattern.match(command):
                self.last_album()
            elif help_pattern.match(command):
                self.base_frame.display_info(commands_list, example_list)

                
    def next_album(self, releases, tracks):
        """
        Display the next directory / album
        """
        for directory, release_info in releases.items():
            self.base_frame.display_meta(release_info, tracks)


    def last_album(self):
        """
        There are no more albums in this direction - display the quit button
        """
        self.quit_command = True
        self.base_frame.quit_command()
        
  
def main():
    if len(sys.argv) < 2:
        print('asdkj')
        exit(2)
        
        
    directory = sys.argv[1]
        
    controller = MetaController(directory)

main()
