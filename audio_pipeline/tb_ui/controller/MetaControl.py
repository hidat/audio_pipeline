from ..model import Model
from ..view import App
from ..view import Dialog
from ...util import Util
from . import EntryController
from ..util import InputPatterns
from ..util import Resources
import shutil
import os
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
        self.mbid_dir = None
        self.picard_dir = None
        self.app = App.App(self.process_input, self.choose_dir, self.last_album)
        self.app.bind("<Escape>", self.last_album)
        
        if root_dir:
            self.choose_dir(root_dir)
        else:
            self.app.after_idle(func=self.app.choose_dir)

    def process_input(self, input_string):
        """
        Process user input

        :param event:
        :return:
        """
        tracks = InputPatterns.track_meta_pattern.match(input_string)
        nav = InputPatterns.nav_pattern.match(input_string)
        popup = InputPatterns.popup_pattern.match(input_string)
        self.app.select_input()
        if tracks:
            # input is (probably) track metadata (currently only RED DOT, YELLOW DOT, CLEAN EDIT, clear)
            try:
                track_nums = tracks.group(InputPatterns.tracknum_acc)
                if re.search("all", track_nums):
                    track_nums = self.model.track_nums()
                else:
                    track_nums = re.findall("\d+", track_nums)
                    track_nums = set([int(track_num) for track_num in track_nums])
                value = tracks.group(InputPatterns.meta_acc)
                self.new_meta_input(track_nums, value)
            except ValueError as e:
                print(e)
                err_msg = "Invalid input " + str(input_string)
                Dialog.err_message(err_msg, None, parent=self.app)
        elif nav:
            self.navigate(nav)
        elif popup:
            self.popup(popup)
        else:
            err_msg = "Invalid input " + str(input_string)
            Dialog.err_message(err_msg, None, parent=self.app)

    def new_meta_input(self, track_nums, value):
        """
        When we have input we've determined is (probably) metadata,
        add it to the metadata of the specified track
        """
        red = InputPatterns.red_dot.match(value)
        yellow = InputPatterns.yellow_dot.match(value)
        clean = InputPatterns.clean_edit.match(value)
        clear = InputPatterns.rm_rating.match(value)
        if not (red or yellow or clean or clear):
                err_msg = "Invalid Input " + str(value)
                Dialog.err_message(err_msg, None, parent=self.app)
                return None

        # we have a valid metadata input - go through tracks in release &
        # update the ones with the specified track number
        for track in self.model.current_release:
            if track.track_num.value in track_nums:
                # update this track's metadata
                if red:
                    track.kexp.save_obscenity(Util.Obscenity.red)
                elif yellow:
                    track.kexp.save_obscenity(Util.Obscenity.yellow)
                elif clean:
                    track.kexp.save_obscenity(Util.Obscenity.clean)
                elif clear:
                    track.kexp.save_obscenity(None)
                self.app.update_meta(track)
                track_nums.remove(track.track_num.value)

        # any leftover track numbers are not valid - display an error message
        for track in track_nums:
            err_msg = "Invalid Track Number: " + str(track)
            Dialog.err_message(err_msg, None, parent=self.app)
            
    def navigate(self, command):
        """
        Change the album displayed.
        """
        jump = command.group(InputPatterns.jump)
        
        if command.group(InputPatterns.next):
            if jump:
                tracks = self.model.jump(int(jump))
                self.app.display_meta(tracks)
            elif self.model.has_next():
                self.next_album()
            else:
                self.last_album()
        elif command.group(InputPatterns.prev):
            if jump:
                tracks = self.model.jump((-1 *int(jump)))
                self.app.display_meta(tracks)
            elif self.model.has_prev():
                self.prev_album()
            else:
                self.last_album()
            
    def popup(self, command):
        """
        Open the appropriate popup, as determined by the command
        """
        if command.group(InputPatterns.edit):
            meta_entry = EntryController.Entry(self.model.current_release, self.app, self.update_album)
            meta_entry.start()        
        elif command.group(InputPatterns.quit):
            self.last_album()        
        elif command.group(InputPatterns.help):
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
        tracks = self.model.next()
        self.app.display_meta(tracks)

    def prev_album(self):
        """
        Display the previous album's metadata
        """
        tracks = self.model.prev()
        self.app.display_meta(tracks)

    def last_album(self, event=None):
        """
        Display a 'quit'? dialog
        """
        Dialog.Check(self.app, "Processing complete", "Close TB", self.close, self.app.quit, "Close TomatoBanana?")

    def close(self):
        """
        Close TomatoBanana; move files into appropriate folders
        """
        self.model.first()
        
        while self.model.has_next():
            release = self.model.next()

            # get path to has-mbid and no-mbid folders once per release
            release_path = os.path.split(release[0].file_name)[0]
            picard = release[0].picard
            mb = release[0].mb
            if not os.path.exists(picard):
                os.mkdir(picard)
            if not os.path.exists(mb):
                os.mkdir(mb)
            
            for track in release:
                # move to correct folder
                shutil.move(track.file_name, track.dest_dir)
                
                
            try:
                os.rmdir(picard)
            except OSError as e:
                print("picard)")
                
            try:
                os.rmdir(mb)
            except OSError as e:
                print("mb")
                
            try:
                os.rmdir(release_path)
            except OSError as e:
                # release directory is not empty
                continue

                


        self.app.quit()

        
    def choose_dir(self, root_dir):
        if root_dir > "":
            new_model = Model.ProcessDirectory(root_dir)
            if new_model.has_next():
            
                path, releases = os.path.split(root_dir)
                self.mbid_dir = os.path.join(path, Resources.mbid_directory)
                    
                self.picard_dir = os.path.join(path, Resources.picard_directory)
            
            
                self.root_dir = root_dir
                self.model = new_model
                self.next_album()
            else:
                if not self.root_dir:
                    Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                     {"name": "Cancel", "command": self.app.quit}])
                else:
                    Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                     {"name": "Cancel"}], master=self.app)
        else:
            if not self.root_dir:
                Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                  {"name": "Cancel", "command": self.app.quit}])
            else:
                Dialog.DialogBox("Please select a valid directory.", buttons=[{"name": "OK", "command": self.app.choose_dir},
                                 {"name": "Cancel"}], master=self.app)