import tkinter.tix as tk
from . import Dialog

class MetaGrid(tk.Grid):

    def __init__(self, update_command, last_command, start_index,
                 forbidden_rows, forbidden_columns, *args, **kwargs):
        
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.update_command = update_command
        self.last_command = last_command
        if 'width' in kwargs and 'height' in kwargs:
            self.start = start_index
            self.final = (int(self['width']) - 1, int(self['height']) - 1)
            
        self.forbidden_rows = forbidden_rows
        self.forbidden_columns = forbidden_columns
        self.curr_pos = self.start
        self.curr_meta = ""
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        
        # There has got to be a better way to bind tab and return to the selected cell entry
        # But I haven't found it yet! So this is what we'll do for now.
        x = int(x)
        y = int(y)
        success = True
        self.bind_class("Entry", "<Tab>", self.tab_press)
        self.bind_class("Entry", "<Return>", self.enter_press)
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        good_meta = self.update_command(pos, meta)
        if good_meta:
            self.curr_pos = (x, y)
        else:
            self.set_curr_cell(pos[0], pos[1])
        return success

    def enter_press(self, event):
        # (possibly) update metadata
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        good_meta = self.update_command(pos, meta)
        if good_meta:
            self.enter_press_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.enter_press_innards()
                pos = self.curr_pos
        else:
            self.set(pos[0], pos[1], text=meta)
        return "break"
        
    def tab_press(self, event):
        # (possibly) update metadata
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        good_meta = self.update_command(pos, meta)
        if good_meta:
            self.tab_press_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.tab_press_innards()
                pos = self.curr_pos
        else:
            self.set(pos[0], pos[1], text=meta)
        return "break"
        
    def enter_press_innards(self):
        # check if we need to update metadata
        print("enter " + str(self.curr_pos))
        if self.curr_pos == self.final:
            # call a passed method
            self.last_command()
        elif self.curr_pos[1] == int(self['height']) - 1:
            # loop to the start of the next column
            self.curr_pos = (self.curr_pos[0] + 1, self.start[1])
        else:
            # not at the end of the grid or the end of the column - just move down one row
            self.curr_pos = (self.curr_pos[0], self.curr_pos[1] + 1)
            
        if self.curr_pos:
            self.set_curr_cell()
            
    def tab_press_innards(self):
        print("tab " + str(self.curr_pos))
        if self.curr_pos == self.final:
            # call the psased 'final' method
            # behavior in the final cell is the same for return and tab
            self.last_command()
        elif self.curr_pos[0] == int(self['width']) - 1:
            # loop to the start of the next row
            self.curr_pos = (self.start[0], self.curr_pos[1] + 1)
        else:
            # not at the end of the grid or the end of the row
            # just move over one column (in the same row)
            self.curr_pos = (self.curr_pos[0] + 1, self.curr_pos[1])
            
        if self.curr_pos:
            self.set_curr_cell()
            
    def set_curr_cell(self):
        self.anchor_set(self.curr_pos[0], self.curr_pos[1])
        self.edit_set(self.curr_pos[0], self.curr_pos[1])
 
        
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

        # set up grid for the release metadata
        self.release = MetaGrid(update_command=control.check_release, last_command=self.release_end,
                                start_index=(0, 1), forbidden_rows = [0], forbidden_columns=[],
                                master=self, name="release_grid", width=len(control.release_categories),
                                height=2, selectunit="cell")

        # set up the release grid
        for name, tag in control.release:
            if tag.release:
                col = control.release_categories.index(name)
                if name == "Album Artist":
                    self.release.size_column(index=col, size=200)
                elif name == "Album":
                    self.release.size_column(index=col, size=250)
                else:
                    self.release.size_column(index=col, size=75)

                self.release.size_column(index=col, pad0=5, pad1=5)

                self.release.set(col, 0, text=name)
                self.release.set(col, 1, text=str(tag.value))

        # set up the track grid
        self.tracks = MetaGrid(update_command=control.check_track, last_command=self.track_end,
                               start_index=(1,1), forbidden_rows = [0], forbidden_columns = [0, 3],
                               master=self, name="track_grid", width=len(control.track_categories),
                               height=len(control.tracks)+1, selectunit="cell")

        for name in control.track_categories:
            col = control.track_categories.index(name)
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
            for name, tag in track:
                if not tag.release:
                    self.tracks.set(col, row, text=str(tag.value))
                    col += 1
            row += 1

        # ask if user wants to save on close
        self.protocol("WM_DELETE_WINDOW", self.quit_popup)

    def save(self):
        self.__save()
        self.unbind_class("Entry", "<Tab>")
        self.unbind_class("Entry", "<Return>")
        self.destroy()

    def quit_popup(self):
        quit_display = Dialog.DialogBox("Save metadata changes?", master=self)
        buttons = [{"name": "Save", "command": self.save}, {"name": "Close Without Saving", "command": self.destroy}]
        quit_display.button_box(buttons)
        
    def track_end(self):
        # right now we're just looping, but should move down to the 'save and quit' button in reality
        self.tracks.curr_pos = None
        self.release.curr_pos = self.release.start
        self.release.anchor_set(self.release.curr_pos[0], self.release.curr_pos[1])
        self.release.edit_set(self.release.curr_pos[0], self.release.curr_pos[1])
        
    def release_end(self):
        # called when tab / return is pressed in the last cell of the release meta grid
        self.release.curr_pos = None
        self.tracks.curr_pos = self.tracks.start
        self.tracks.anchor_set(self.tracks.curr_pos[0], self.tracks.curr_pos[1])
        self.tracks.edit_set(self.tracks.curr_pos[0], self.tracks.curr_pos[1])
        
    def startup(self):
        # label for track metadata
        l = tk.Label(self, name="track_label", text="Track Metadata")
        # finish & save button
        quit_button = tk.Button(self, text="Finish Entry", command=self.quit_popup)

        self.release.pack()
        l.pack()
        self.tracks.pack()
        quit_button.pack()

        self.release.anchor_set(self.release.start[0], self.release.start[1])
        self.release.edit_set(self.release.start[0], self.release.start[1])

