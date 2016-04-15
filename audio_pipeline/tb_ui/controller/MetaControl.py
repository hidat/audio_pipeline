from ..model import MetaModel
from ..view import App
from ..view import Dialog
from ...util import Util
from . import EntryController
from ..util import InputPatterns
import re


class MetaController:

    def __init__(self, root_dir):
        """
        MetaControl is in charge of sending commands to the view & getting information from the model
        Runs the TomatoBanana app

        :param root_dir: Base directory to look for audio files in
        :return:
        """
        self.model = None
        self.root_dir = None
        self.app = App.App(self.process_input, self.choose_dir)
        self.app.bind("<Escape>", self.last_album)

        if root_dir:
            self.model = MetaModel.ProcessDirectory(root_dir)
            self.root_dir = root_dir

            if self.model.has_next():
                self.next_album()
        else:
            self.app.after_idle(func=self.app.choose_dir)

    def process_input(self, event):
        """
        Process user input

        :param event:
        :return:
        """
        input_string = self.app.get_input()
        tracks = InputPatterns.track_meta_pattern.match(input_string)
        release = InputPatterns.release_meta_pattern.match(input_string)
        tag = InputPatterns.tag_pattern.match(input_string)
        self.app.select_input()
        if tracks:
            # input is (probably) track metadata (currently only RED DOT, YELLOW DOT)
            try:
                track_nums = tracks.group(InputPatterns.tracknum_acc)
                if re.search("all", track_nums):
                    track_nums = set(self.model.track_nums())
                else:
                    track_nums = re.findall("\d+", track_nums)
                    track_nums = set([int(track_num) for track_num in track_nums])
                value = tracks.group(InputPatterns.meta_acc)
                self.new_meta_input(track_nums, value)
            except ValueError as e:
                print(e)
                err_msg = "Invalid input " + str(input_string)
                Dialog.err_message(err_msg, None, parent=self.app)
        elif release:
            self.app.select_release()
        elif input_string > '':
            command = input_string.split()[0]
            self.process_command(command)

    def new_meta_input(self, track_nums, value):
        """
        When we have input we've determined is (probably) metadata,
        add it to the metadata of the specified track
        """
        tracks = []
        
        red = InputPatterns.red_dot.match(value)
        yellow = InputPatterns.yellow_dot.match(value)
        clear = InputPatterns.rm_rating.match(value)
        if not red and not yellow and not clear:
                err_msg = "Invalid Input " + str(value)
                Dialog.err_message(err_msg, None, parent=self.app)
                return None

        # we have a valid metadata input - go through tracks in release &
        # update the ones with the specified track number
        for track in self.model.current_release:
            if track.track_num.value in track_nums:
                # get track filename
                tracks.append(track.file_name)
                # update this track's metadata
                if red:
                    track.kexp.save_obscenity(Util.Obscenity.red)
                elif yellow:
                    track.kexp.save_obscenity(Util.Obscenity.yellow)
                elif clear:
                    track.kexp.save_obscenity(None)
                self.app.update_meta(track)
                track_nums.remove(track.track_num.value)

        # any leftover track numbers are not valid - display an error message
        for track in track_nums:
            err_msg = "Invalid Track Number: " + str(track)
            Dialog.err_message(err_msg, None, parent=self.app)
        self.app.select_tracks(tracks)
            
    def process_command(self, command):
        """
        Changes the album metadata on screen to the previous or next in the directory list,
        depending on the command that is passed in.
        """
        if InputPatterns.entry_pattern.match(command):
            meta_entry = EntryController.Entry(self.model.current_release, self.app, self.update_album)
            meta_entry.start()
        elif InputPatterns.next_pattern.match(command):
            if self.model.has_next():
                self.next_album()
            else:
                self.last_album()
        elif InputPatterns.prev_pattern.match(command):
            if self.model.has_prev():
                self.prev_album()
            else:
                self.last_album()
        elif InputPatterns.done_pattern.match(command):
            self.last_album()
        elif InputPatterns.help_pattern.match(command):
            self.app.display_info()

    def update_album(self):
        """
        Update current release metadata
        """
        for track in self.model.current_release:
            self.app.update_meta(track)
            
    def next_album(self):
        """
        Display the next directory / album
        """
        tracks = self.model.get_next()
        self.app.display_meta(tracks)

    def prev_album(self):
        """
        Display the previous album's metadata
        """
        tracks = self.model.get_prev()
        self.app.display_meta(tracks)

    def last_album(self, event=None):
        """
        Display a 'quit'? dialog
        """
        Dialog.quit_message("Close TomatoBanana?", self.app.quit, self.app)
  
    def choose_dir(self, root_dir):
        if root_dir > "":
            new_model = MetaModel.ProcessDirectory(root_dir)
            if new_model.has_next():
                self.root_dir = root_dir
                self.model = new_model
                self.next_album()
            else:
                if not self.root_dir:
                    Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                     {"name": "Cancel", "command": self.app.quit}])
                else:
                    Dialog.err_message("Please select a valid directory.", self.app.choose_dir, quit=True)
        else:
            if not self.root_dir:
                Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                  {"name": "Cancel", "command": self.app.quit}])
            else:
                Dialog.err_message("Please select a valid directory.", self.app.choose_dir, quit=True)