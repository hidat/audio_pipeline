import tkinter.tix as tk
from . import Settings, MetaFrame, InfoFrame, InputFrame, Dialog, Setup
from ..util import Resources


class App(tk.Tk):

    def __init__(self, input_processor, directory_selector, close_command):
    
        self.input_processor = input_processor
        self.directory_selector = directory_selector
        self.close_command = close_command

        release_row = 0
        release_column = 0
        self.release_location = (1, 1)
        self.track_location = (2, 1)
        self.input_location = (3, 1)

        tk.Tk.__init__(self)
        height_frame = tk.Frame(master=self, bg=Settings.bg_color, height=80*8, width=0)
        height_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=3, sticky="nw")
        main_frame = tk.Frame(master=self, bg=Settings.bg_color)
        main_frame.grid(row=0, column=1, sticky="nw")
        self['bg'] = Settings.bg_color
        self.title("TomatoBanana")

        self.processing_done = tk.IntVar()
        self.processing_done.set(Resources.cancel)
        
        self.release_frame = MetaFrame.ReleaseFrame(main_frame)
        self.track_frame = MetaFrame.TrackFrame(main_frame)
        self.input_frame = InputFrame.InputFrame(input_processor)
        self.info_window = None

        self.release_frame.grid(row=release_row, column=release_column, sticky="nw")
        self.track_frame.grid(row=release_row + 1, column=release_column, sticky="nw")
        self.input_frame.grid(row=1, column=1, sticky="sw")

        self.menubar = tk.Menu(self)
        self.menubar.add_command(label="Change Directory", command=self.choose_dir)
        self.menubar.add_separator()
        self.menubar.add_command(label="Help", command=self.display_info)
#         self.menubar.add_separator()
#         self.menubar.add_command(label="Settings", command=self.show_setup)
        self.config(menu=self.menubar)

        self.protocol("WM_DELETE_WINDOW", self.close_command)

        self.allow_input()
        self.grid()

    def show_setup(self):
        setup = Setup.App()
        setup.protocol("WM_DELETE_WINDOW", setup.destroy)

    def choose_dir(self):
        """
        Select an appropriate directory to display metadata from
        """
        Dialog.choose_dir(self.directory_selector, master=self)

    def display_meta(self, track_meta):
        self.release_frame.display_meta(track_meta)
        self.track_frame.display_meta(track_meta)

    def update_meta(self, track_meta):
        if type(track_meta) == list:
            self.release_frame.update_meta(track_meta[0])
            for t in track_meta:
                self.track_frame.update_meta(t)
        else:
            self.release_frame.update_meta(track_meta)
            self.track_frame.update_meta(track_meta)

    def display_info(self):
        if self.info_window:
            self.info_window.focus_set()
        else:
            self.info_window = tk.Toplevel()
            self.info_window.title("Help")
            self.info_window["bg"] = Settings.bg_color
            info = InfoFrame.InfoFrame(master=self.info_window, base_name = "Help | ")
#             info.display_commands()
            self.info_window.protocol("WM_DELETE_WINDOW", self.close_info)

    ######################
    #   Input Processing
    ######################

    def allow_input(self):
        self.input_frame.allow_input()
        self.input_frame.nav_buttons()

    def get_input(self):
        return self.input_frame.get_input()

    def clear_input(self):
        self.input_frame.clear_input()

    def select_input(self):
        self.input_frame.select_input()

    ######################

    def close_info(self):
        self.info_window.destroy()
        self.info_window = None
        
    def move_files(self, move):
        if move is not None:
            self.processing_done.set(move)
        
    def quit(self):
        self.after(40, self.destroy)

    ####

    def select_tracks(self, tracks):
        if self.track_frame:
            self.track_frame.select_tracks(tracks)

    def select_release(self):
        if self.release_frame:
            self.release_frame.select_release()