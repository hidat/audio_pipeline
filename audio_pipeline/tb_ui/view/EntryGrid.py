import tkinter.tix as tk
from . import Dialog

class MetaGrid(tk.Grid):

    def __init__(self, update_command, last_command, bindings, start_index,
                 forbidden_rows, forbidden_columns, *args, **kwargs):
        kwargs['editdone'] = self.edit_done
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.update_command = update_command
        self.last_command = last_command
        if 'width' in kwargs and 'height' in kwargs:
            self.start = start_index
            self.final = (int(self['width']) - 1, int(self['height']) - 1)
            
        self.bindings = bindings
        self.forbidden_rows = forbidden_rows
        self.forbidden_columns = forbidden_columns
        self.curr_pos = self.start
        self.curr_meta = ""
        
    def edit_done(self, x, y):
        print("DONE EDITING " + x + " " + y)
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        
        # There has got to be a better way to bind tab and return to the selected cell entry
        # But I haven't found it yet! So this is what we'll do for now.
        x = int(x)
        y = int(y)
        success = True
        if not self.bindings():
            self.bind_class("Entry", "<Key-Tab>", self.right)
            self.bind_class("Entry", "<Key-Return>", self.down)
            self.bind_class("Entry", "<Key-Up>", self.up)
            self.bind_class("Entry", "<Key-Down>", self.down)
            self.bind_class("Entry", "<Shift-Tab>", self.left)
            self.bind_class("Entry", "<Shift-Left>", self.left)
            self.bind_class("Entry", "<Shift-Right>", self.right)
            self.bind_class("Entry", "<Shift-Up>", self.up)
            self.bind_class("Entry", "<Shift-Down>", self.down)
        good_meta = self.move()
        if good_meta:
            self.curr_pos = (x, y)
        else:
            self.set_curr_cell()
        return success
        
    def move(self):
        success = False
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        good_meta = self.update_command(pos, meta)
        if good_meta:
            success = True
        else:
            self.set(pos[0], pos[1], text=meta)
        return success
        
    def left(self, event):
        success = self.move()
        
        if success:
            self.left_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.left_innards()
                pos = self.curr_pos
        return "break"
        
    def up(self, event):
        success = self.move()
        
        if success:
            self.up_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.up_innards()
                pos = self.curr_pos
        return "break"
        
    def down(self, event):
        success = self.move()
        if success:
            self.down_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.down_innards()
                pos = self.curr_pos
        return "break"
    
    def right(self, event):
        success = self.move()
        if success:
            self.right_innards()
            pos = self.curr_pos
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                self.right_innards()
                pos = self.curr_pos
        return "break"
        
    def up_innards(self):
        # check if we need to update metadata
        if self.curr_pos == self.start:
            # going up we will not loop????
            self.curr_pos = self.curr_pos
        elif self.curr_pos[1] == 1:
            # At top of column - loop to end of previous column
            self.curr_pos = (self.curr_pos[0] - 1, int(self['height']) - 1)
        else:
            # not at the end of the grid or the end of the column - just move up one row
            self.curr_pos = (self.curr_pos[0], self.curr_pos[1] - 1)
            
        if self.curr_pos:
            self.set_curr_cell()
        
    def down_innards(self):
        # check if we need to update metadata
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
            
    def right_innards(self):
        if self.curr_pos == self.final:
            # call the passed 'final' method
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
            
    def left_innards(self):
        if self.curr_pos == self.start:
            # right now we're just gonna not move
            self.curr_pos = self.curr_pos
        elif self.curr_pos[0] == self.start[0]:
            # loop to the end of the previous row
            self.curr_pos = (int(self['width']) - 1, self.curr_pos[1] - 1)
        else:
            # not at the end of the grid or the end of the row
            # move one column to the left (in the same row)
            self.curr_pos = (self.curr_pos[0] - 1, self.curr_pos[1])
            
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
        self.the_end = control.quit

        # set up grid for the release metadata
        self.release = MetaGrid(update_command=control.check_release, last_command=self.release_end, bindings=self.bind_release,
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
        self.tracks = MetaGrid(update_command=control.check_track, last_command=self.track_end, bindings=self.bind_tracks,
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
                    if tag.value:
                        self.tracks.set(col, row, text=str(tag.value))
                    else:
                        self.tracks.set(col, row, text="")
                    col += 1
            row += 1
            
            
        self.quit_button = tk.Button(self, text="Finish Entry", command=self.quit_popup)
        self.quit_button.bind("<Return>", self.quit_button["command"])
        self.quit_button.bind("<Tab>", self.starting_selection)
        # ask if user wants to save on close
        self.protocol("WM_DELETE_WINDOW", self.quit_popup)
        self.release_bindings = False

    def save(self):
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
        self.after(100, self.the_end)
        
    def quit_popup(self):
        quit_display = Dialog.DialogBox("Save metadata changes?", master=self)
        buttons = [{"name": "Save", "command": self.save}, {"name": "Close Without Saving", "command": self.quit}]
        quit_display.button_box(buttons)
        
    def starting_selection(self):
        self.release.curr_pos = self.release.start
        self.release.anchor_set(self.release.start[0], self.release.start[1])
        self.release.edit_set(self.release.start[0], self.release.start[1])

    def track_end(self):
        # right now we're just looping, but should move down to the 'save and quit' button in reality
        self.tracks.curr_pos = None
        self.quit_button.focus_set()

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