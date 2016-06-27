import tkinter.tix as tk
from . import Dialog
from . import MetaGrid
from ..util import InputPatterns
import re


class EntryGrid(tk.Toplevel):

    def __init__(self, control, master=None):
        """
        :param release: Current release metadata
        :param track_meta: Current track metadata
                           Dictionary of track filename -> (tag name-> tag)
        """
        tk.Toplevel.__init__(self, master=master)
        self.title("Metadata Entry Friend")
        self.__save = control.save
        self.the_end = control.quit
        self.release_categories = [tag.name for tag in control.release]
        self.track_categories = [tag.name for tag in control.track]

        # set up grid for the release metadata
        self.release = MetaGrid.MetaGrid(update_command=control.check_release, last_command=self.release_end, bindings=self.bind_release,
                                start_index=(0, 1), forbidden_rows = [0], forbidden_columns=[],
                                master=self, name="release_grid", width=len(self.release_categories),
                                height=2, selectunit="cell")

        # set up the release grid
        for tag in control.release:
            name = tag.name
            col = self.release_categories.index(name)
            if name == "Album Artist" or name == "MBID":
                self.release.size_column(index=col, size=200)
            elif name == "Album":
                self.release.size_column(index=col, size=250)
            elif name == "Label":
                self.release.size_column(index=col, size=200)
            else:
                self.release.size_column(index=col, size=75)

            self.release.size_column(index=col, pad0=5, pad1=5)

            self.release.set(col, 0, text=name)
            if tag.value:
                self.release.set(col, 1, text=str(tag.value))
            else:
                self.release.set(col, 1, text=str(" "))

        # set up the track grid
        self.tracks = MetaGrid.MetaGrid(update_command=control.check_track, last_command=self.track_end, bindings=self.bind_tracks,
                               start_index=(1,1), forbidden_rows = [0], forbidden_columns = [0, 3],
                               master=self, name="track_grid", width=len(self.track_categories),
                               height=len(control.tracks)+1, selectunit="cell")

        for name in self.track_categories:
            col = self.track_categories.index(name)
            if name == "Title":
                self.tracks.size_column(index=col, size=250)
            elif name == "Artist":
                self.tracks.size_column(index=col, size=200)
            elif name == "KEXPFCCOBSCENITYRATING":
                self.tracks.size_column(index=col, size=150)
            else:
                self.tracks.size_column(index=col, size=75)

            self.tracks.size_column(index=col, pad0=5, pad1=5)

            self.tracks.set(col, 0, text=name)
                        
        row = 1
        for track in control.tracks:
            col = 0
            for tag in track.track():
                if tag.name in self.track_categories:
                    if tag.value:
                        self.tracks.set(col, row, text=str(tag.value))
                    else:
                        self.tracks.set(col, row, text=" ")
                    col += 1
            row += 1

        self.quit_button = tk.Button(self, text="Finish & Save", command=self.quit_popup)
        self.quit_button.bind("<Return>", self.quit_button["command"])
        self.quit_button.bind("<Tab>", self.starting_selection)
        self.bind("<Escape>", self.quit_popup)
        # ask if user wants to save on close
        self.protocol("WM_DELETE_WINDOW", self.quit_popup)
        self.release_bindings = False

        self.grab_set()

    def save(self):
        self.release.editapply()
        self.tracks.editapply()
        self.__save()
        self.quit()

    def quit(self):
        self.unbind_class("Entry", "<Key-Tab>")
        self.unbind_class("Entry", "<Key-Return>")
        self.unbind_class("Entry", "<Key-Up>")
        self.unbind_class("Entry", "<Key-Down>")
        self.unbind_class("Entry", "<Shift-Tab>")
        self.unbind_class("Entry", "<Shift-Left>")
        self.unbind_class("Entry", "<Shift-Right>")
        self.unbind_class("Entry", "<Shift-Up>")
        self.unbind_class("Entry", "<Shift-Down>")
        self.unbind_class("Entry", "<Control-z>")
        self.after(100, self.the_end)
        
    def quit_popup(self, event=None):
        #check_messages = ["Error in MusicBrainz metadata", "Wrong disc for case", "Burned disc"]
        #quit_display = Dialog.MultiCheck(self, check_messages, )
        quit_display = Dialog.DialogBox("Save metadata changes?", master=self)
        buttons = [{"name": "Save", "command": self.save}, {"name": "Don't Save", "command": self.quit}, {"name": "Cancel"}]
        quit_display.button_box(buttons)
        
    def starting_selection(self, event=None):
        self.release.curr_pos = self.release.start
        self.release.set_curr_cell()

    def track_end(self):
        # right now we're just looping, but should move down to the 'save and quit' button in reality
        self.tracks.curr_pos = None
        self.quit_button.focus_set()

    def release_end(self):
        # called when tab / return is pressed in the last cell of the release meta grid
        self.release.curr_pos = None
        self.tracks.curr_pos = self.tracks.start
        self.tracks.set_curr_cell()
        
    def startup(self):
        # label for track metadata
        l = tk.Label(self, name="track_label", text="Track Metadata")
        # finish & save button

        self.release.pack()
        l.pack()
        self.tracks.pack()
        self.quit_button.pack()
        
        self.after(100, self.starting_selection)
        
    def bind_tracks(self):
        tracks = True
        if self.release_bindings:
            self.release_bindings = False
            tracks = False
        return tracks
    
    def bind_release(self):
        release = True
        if not self.release_bindings:
            self.release_bindings = True
            release = False
        return release
        
    def track_artist_set(self, album_artist):
        # should probably change this because strings are terrible
        artist_column = self.track_categories.index('Artist')
        aa = self.release.curr_meta # will do this better, sometime, probably
        for y in range(0, int(self.tracks['height'])):
            artist = self.tracks.entrycget(artist_column, y, 'text')
            if re.match(aa, artist):
                self.tracks.set(artist_column, y, text=(re.sub(aa, album_artist, artist)))
            elif InputPatterns.whitespace.match(artist) or\
               InputPatterns.unknown.match(artist):
                # set track artist to album artist
                self.tracks.set(artist_column, y, text=album_artist)