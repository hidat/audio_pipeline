from ..model import Model
from ..view import App
from ..view import Dialog
from ...util import Util
from . import EntryController
from ..util import InputPatterns
from ..util import Resources
import time
import os


class TBController:

    def __init__(self, root_dir, copy_dir):
        """
        MetaControl is in charge of sending commands to the view & getting information from the model
        Runs the TomatoBanana app

        :param root_dir: Base directory to look for audio files in
        :return:
        """
        self.model = None
        self.root_dir = None
        self.copy_dir = copy_dir
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
            # input is (probably) track metadata (currently only RED DOT, YELLOW DOT, CLEAN EDIT, clear (l))
            try:
                track_nums = InputPatterns.get_track_numbers(tracks.group())
                if "all" in track_nums:
                    track_nums = self.model.track_nums()
                value = tracks.group(InputPatterns.meta_acc)
                self.new_meta_input(track_nums, value)
            except ValueError as e:
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
        obscenity = InputPatterns.obscenity_rating.match(value)
        edit = InputPatterns.radio_edit.match(value)
        clear = InputPatterns.rm_rating.match(value)
        if not (obscenity or edit or clear):
                err_msg = "Invalid Input " + str(value)
                Dialog.err_message(err_msg, None, parent=self.app)
                return None

        # we have a valid metadata input - go through tracks in release &
        # update the ones with the specified track number
        for track in self.model.current_release:
            if track.track_num.value in track_nums:
                # update this tracks metadata
                if obscenity:
                    if obscenity.group(InputPatterns.red):
                        track.obscenity.save(Util.Obscenity.red)
                    elif obscenity.group(InputPatterns.yellow):
                        track.obscenity.save(Util.Obscenity.yellow)
                    elif obscenity.group(InputPatterns.kexp):
                        track.obscenity.save(Util.Obscenity.kexp_clean)
                    elif obscenity.group(InputPatterns.standard):
                        track.obscenity.save(Util.Obscenity.clean)
                if edit:
                    if edit.group(InputPatterns.kexp):
                        track.radio_edit.save(Util.Edits.kexp_edit)
                    elif edit.group(InputPatterns.standard):
                        track.radio_edit.save(Util.Edits.radio_edit)
                if clear:
                    track.obscenity.save(None)
                    track.radio_edit.save(None)
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
        Dialog.Check(None, "Move Files?", "Close TB", self.app.processing_done, "Close TomatoBanana?")
        self.app.wait_variable(self.app.processing_done)
        move_files = self.app.processing_done.get()
        if move_files != Resources.cancel:
            self.app.destroy()
            time.sleep(.5)
            if move_files > 0:
                print('move files')
                self.close()
            del self.model

    def close(self):
        """
        Close TomatoBanana; move files into appropriate folders
        """
        self.model.processing_complete.move_files(self.model)
        
    def choose_dir(self, root_dir):
        if root_dir > "":
        
            if self.copy_dir:
                dest_dir = self.copy_dir
            else:
                dest_dir = os.path.split(root_dir)[0]
                
            new_model = Model.ProcessDirectory(root_dir, dest_dir, False)
            if new_model.has_next():
            
                path, releases = os.path.split(root_dir)
            
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
            self.app.destroy()