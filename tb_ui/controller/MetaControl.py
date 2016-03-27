import tb_ui.model.MetaModel as MetaModel
import tb_ui.view.App as App
import tb_ui.view.Dialog as Dialog
import util.Util as Util
import re

class InputPatterns():
    tracknum_acc = "track_num"
    meta_acc = "meta"
    command_acc = "command"

    track_meta_pattern = re.compile('(?P<' + tracknum_acc + '>(((\d+((,)|(\s))*)+)|(\s*all)))\s*(?P<' + meta_acc + '>.+)')
    command_pattern = re.compile('(?P<' + command_acc + '>.+)')
    
    prev_pattern = re.compile("\s*p(rev)?.*", flags=re.I)
    next_pattern = re.compile("\s*n(ext)?", flags=re.I)
    done_pattern = re.compile("\s*d+(one)?", flags=re.I)
    help_pattern = re.compile("\s*h(elp)?", flags=re.I)
    
    yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
    red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
    rm_rating = re.compile("\s*c(lear)?", flags=re.I)


class MetaController:

    def __init__(self, root_dir):
        """
        MetaControl is in charge of sending commands to the view & getting information from the model
        Runs the TomatoBanana app

        :param root_dir: Base directory to look for audio files in
        :return:
        """
        self.model = None
        self.app = App.App(self.process_input, self.choose_dir)

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
        print(input_string)
        match = InputPatterns.track_meta_pattern.match(input_string)
        if match:
            # input is (probably) track metadata (currently only RED DOT, YELLOW DOT)
            try:
                track_nums = match.group(InputPatterns.tracknum_acc)
                if re.search("all", track_nums):
                    track_nums = set(self.model.track_nums())
                else:
                    track_nums = re.findall("\d+", track_nums)
                    track_nums = set([int(track_num) for track_num in track_nums])
                value = match.group(InputPatterns.meta_acc)
                self.new_meta_input(track_nums, value)
            except ValueError:
                err_msg = "Invalid input " + str(input_string)
                Dialog.err_message(err_msg, None, parent=self.app)
        else:
            command = input_string.split()[0]
            self.change_displayed_album(command)

    def new_meta_input(self, track_nums, value):
        """
        When we have input we've determined is (probably) metadata,
        add it to the metadata of the specified track
        """
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
                # update this track's metadata
                if red:
                    track.kexp.save_obscenity(Util.Obscenity.red)
                elif yellow:
                    track.kexp.save_obscenity(Util.Obscenity.yellow)
                elif clear:
                    track.kexp.save_obscenity(None)
                track.save()
                self.app.update_meta(track)
                track_nums.remove(track.track_num.value)

        # any leftover track numbers are not valid - display an error message
        for track in track_nums:
            err_msg = "Invalid Track Number: " + str(track)
            Dialog.err_message(err_msg, None, parent=self.app)

        self.app.clear_input()
            
    def change_displayed_album(self, command):
        """
        Changes the album metadata on screen to the previous or next in the directory list,
        depending on the command that is passed in.
        """
        if InputPatterns.next_pattern.match(command):
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
                
        self.app.select_input()

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

    def last_album(self):
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
                Dialog.err_message("Please select a valid directory.", self.app.choose_dir, quit=True)
        else:
            Dialog.err_message("Please select a valid directory.", self.app.choose_dir, quit=True)
