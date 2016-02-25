import audio_pipeline.tb_ui.model.MetaModel as MetaModel
import audio_pipeline.tb_ui.view.MetaView as MetaView
import sys
import re

tracknum_acc = "track_num"
meta_acc = "meta"
command_acc = "command"

track_meta_pattern = re.compile('(?P<' + tracknum_acc + '>(((\d+((,)|(\s))*)+)|(\s*all)))\s*(?P<' + meta_acc + '>.+)')
command_pattern = re.compile('(?P<' + command_acc + '>.+)')

class MetaController:

    def __init__(self, root_dir):
        """
        MetaController is in charge of sending commands to the view and getting information from the model.
        
        """
        self.meta_model = None
        self.base_frame = MetaView.AppFrame(self.process_input, self.choose_dir)
        
        if root_dir:
            self.meta_model = MetaModel.process_directory(root_dir)
            self.root_dir = root_dir
            
            if self.meta_model.has_next():
                self.next_album()
        else:
            self.base_frame.after_idle(func=self.base_frame.choose_dir)
            
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
                track_nums = match.group(tracknum_acc)
                if re.search("all", track_nums):
                    track_nums = self.meta_model.current_tracks.keys()
                else:
                    track_nums = re.findall("\d+", track_nums)
                    track_nums = [int(track_num) for track_num in track_nums]
                value = match.group(meta_acc)
                self.new_meta_input(track_nums, value)
            except ValueError:
                MetaView.err_message("Invalid input", None, parent=self.base_frame)
        else:
            command = input_string.split()[0]
            self.change_displayed_album(command)


    def new_meta_input(self, track_nums, value):
        """
        When we have input we've determined is (probably) metadata,
        add it to the metadata of the specified track
        """
        yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
        red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
        rm_rating = re.compile("\s*c(lear)?", flags=re.I)
        
        for track_num in track_nums:
            print(track_num)
            new_meta = None
            if track_num not in self.meta_model.current_tracks.keys():
               file_name = None
               err_msg = "Invalid Track Number: " + str(track_num)
               MetaView.err_message(err_msg, None, parent=self.base_frame)
            else:
                file_name = self.meta_model.current_tracks[track_num]
                if rm_rating.match(value):
                    self.meta_model.delete_metadata(file_name, [kexp_tags["obscenity"]])
                elif yellow_dot.match(value):
                    new_meta = {kexp_tags["obscenity"]: kexp_values["y"]}
                elif red_dot.match(value):
                    new_meta = {kexp_tags["obscenity"]: kexp_values["r"]}
                else:
                    err_msg = "Invalid Input " + str(value)
                    MetaView.err_message(err_msg, None, parent=self.base_frame)
            
            if new_meta:
                self.meta_model.update_metadata(file_name, new_meta)
            
            if file_name:
                meta = self.meta_model.get_track_meta(file_name)
                self.base_frame.update_track(file_name, meta)
            
        self.base_frame.clear_input()
            
    def change_displayed_album(self, command):
        """
        Changes the album metadata on screen to the previous or next in the directory list,
        depending on the command that is passed in.
        """
        
        prev_pattern = re.compile("\s*p(rev)?.*", flags=re.I)
        next_pattern = re.compile("\s*n(ext)?", flags=re.I)
        done_pattern = re.compile("\s*d+(one)?", flags=re.I)
        help_pattern = re.compile("\s*h(elp)?", flags=re.I)
        
        if next_pattern.match(command):
            if self.meta_model.has_next():
                self.next_album()
            else:
                self.last_album()
        elif prev_pattern.match(command):
            if self.meta_model.has_prev():
                self.prev_album()
            else:
                self.last_album()
        elif done_pattern.match(command):
            self.last_album()
        elif help_pattern.match(command):
            self.base_frame.display_info(commands_list, example_list)
                
        self.base_frame.select_input()

                
    def next_album(self):
        """
        Display the next directory / album
        """
        releases, tracks = self.meta_model.get_next_meta()
        for directory, release_info in releases.items():
            self.base_frame.display_meta(release_info, tracks)
            
    def prev_album(self):
        releases, tracks = self.meta_model.get_previous_meta()
        for directory, release_info in releases.items():
            self.base_frame.display_meta(release_info, tracks)


    def last_album(self):
        """
        There are no more albums in this direction - display the quit button
        """
        self.base_frame.quit_command()
        
    def choose_dir(self, root_dir):
        if root_dir > "":
            new_model = MetaModel.process_directory(root_dir)
            if new_model.has_next():
                self.root_dir = root_dir
                self.meta_model = new_model
                self.next_album()
            else:
                MetaView.err_message("Please select a valid directory.", self.base_frame.choose_dir, quit=True)
        else:
            MetaView.err_message("Please select a valid directory.", self.base_frame.choose_dir, quit=True)
        
            
def main():
    directory = None
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
                
    controller = MetaController(directory)
    
    controller.base_frame.mainloop()

main()
