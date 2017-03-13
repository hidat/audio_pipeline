from ..model import Model
from ..view import App, Dialog
from ...util import Util
from . import EntryController
from ..util import InputPatterns, Resources
from ...util import Resources as r
from .. import release_tags, track_tags, general_commands, navigate, get_track_nums, clear_track
import time
import os
from . import Search


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


        self.seeder_file = set()

        if root_dir:
            self.choose_dir(root_dir)
        else:
            self.app.after_idle(func=self.app.choose_dir)

    def clean_temp_files(self):
        deleted = set()
        for fname in self.seeder_file:
            try:
                os.remove(fname)
                deleted.add(fname)
            except PermissionError:
                print("Can't close this file")
        for fname in deleted:
            self.seeder_file.remove(fname)

    def process_input(self, input_string):
        """
        Process user input

        :param event:
        :return:
        """
        # if we had a temp file open (seeding mb), delete it -
        # probably safe, since someone has entered a new input
        if self.seeder_file:
            self.clean_temp_files()

        self.app.select_input()

        # check for release tags
        for tag in release_tags:
            release_tag, release_value = tag.execute(input_string)
            if release_tag is not None:
                if release_value is True and self.model.current_release[0].release_tags[release_tag].value:
                    release_value = None
                self.model.set_release_tag(release_tag, release_value)
                self.app.update_meta(self.model.current_release)
                return
            elif release_value is not None:
                err_msg = "Invalid input " + str(input_string)
                Dialog.err_message(err_msg, None, parent=self.app)
                return

        track_nums, input_string = get_track_nums(input_string)
        if track_nums is not None:
            clear = False
            if clear_track[0]:
                clear = clear_track[0].execute(input_string)

            for tag in track_tags:
                if clear:
                    input_string = tag.command
                track_tag, track_value = tag.execute(input_string)
                if track_tag:
                    for track in self.model.current_release:
                        if track.track_num.value in track_nums or 'all' in track_nums:
                            if track_value is True and track.track_tags[track_tag].value:
                                track.track_tags[track_tag].value = None
                            else:
                                track.track_tags[track_tag].value = track_value
                            track.save()
                            self.app.update_meta(track)
                    if not clear:
                        break
            track_nums = track_nums - {'all'} - self.model.track_nums()
            if len(track_nums) > 0:
                for track in track_nums:
                    err_msg = "Invalid Track Number: " + str(track)
                    Dialog.err_message(err_msg, None, parent=self.app)
            return

        nav = navigate(input_string)
        if nav is not None:
            if nav > 0 and not self.model.has_next():
                self.last_album()
            elif nav < 0 and not self.model.has_prev():
                self.last_album()
            else:
                tracks = self.model.jump(nav)
                self.app.display_meta(tracks)
            return

        popup = InputPatterns.popup_pattern.match(input_string)
        genre = InputPatterns.secondary_genre_pattern.match(input_string)
        if Util.is_mbid(input_string):
            complete = self.model.set_mbid(input_string)
            print(complete)
            self.app.update_meta(self.model.current_release)
        elif popup:
            self.popup(popup)
        elif genre:
            genre.group(InputPatterns.meta_acc)
            full_genre = r.Genres.get(genre.group(InputPatterns.meta_acc))
            if full_genre:
                self.model.set_genre(full_genre)
                self.app.update_meta(self.model.current_release[0])
            else:
                err_msg = "Invalid genre " + str(genre.group(InputPatterns.meta_acc))
                Dialog.err_message(err_msg, None, parent=self.app)
        else:
            complete = None
            for command in general_commands:
                complete = command.execute(input_string, self.model)
                if complete:
                    self.app.update_meta(self.model.current_release)
                    break
            if complete is None:
                err_msg = "Invalid input " + str(input_string)
                Dialog.err_message(err_msg, None, parent=self.app)

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
        self.app.update_meta(self.model.current_release)

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
        set_variable = self.app.processing_done
        if self.model.processing_complete:
            Dialog.Check(None, "Move Files?", "Close TB", set_variable, "Close TomatoBanana?")
            self.app.wait_variable(set_variable)
            move_files = set_variable.get()
            print(move_files)
            if move_files != Resources.cancel:
                self.app.destroy()
                time.sleep(.5)
                if move_files > 0:
                    print('move files')
                    self.close()
                del self.model
        else:
            Dialog.DialogBox("Close TomatoBanana?", buttons=[{"name": "OK", "command": lambda: set_variable.set(Resources.checked)},
                             {"name": "Cancel", "command": lambda: set_variable.set(Resources.cancel)}], master=self.app)
            self.app.wait_variable(set_variable)
            close_tb = set_variable.get()
            if close_tb != Resources.cancel:
                self.app.destroy()
                time.sleep(.5)
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
