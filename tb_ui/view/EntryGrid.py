import tkinter.tix as tk
from Util import *
import MetaModel

class MetaGrid(tk.Grid):

    def __init__(self, update_command, last_command, start_index, 
        forbidden_rows, forbidden_columns, *args, **kwargs):
        
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.update_command = update_command
        self.last_command = last_command
        if 'width' in kwargs and 'height' in kwargs:
            self.start =  start_index
            self.final = (int(self['width']) - 1, int(self['height']) - 1)
            
        self.forbidden_rows = forbidden_rows
        self.forbidden_columns = forbidden_columns
        self.curr_pos = self.start
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        
        # There has got to be a better way to bind tab and return to the selected cell entry
        # But I haven't found it yet! So this is what we'll do for now.
        x = int(x)
        y = int(y)
        self.bind_class("Entry", "<Tab>", self.tab_press)
        self.bind_class("Entry", "<Return>", self.enter_press)
        self.curr_pos = (x, y)
        if y in self.forbidden_rows:
            return False
        elif x in self.forbidden_columns:
            return False
        else:
            return True
            
    def tab_press(self, event):
        # (possibly) update metadata 
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        if meta > "":
            improper = self.update_command(pos, meta)
            if improper:
                self.set(pos[0], pos[1], text=meta)
        
        self.tab_press_innards()
        pos = self.curr_pos
        while pos and (pos[0] in self.forbidden_columns \
            or pos[1] in self.forbidden_rows):
            self.tab_press_innards()
            
        return "break"
        
    def enter_press(self, event):
        # (possibly) update metadata
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        if meta > "":
            improper = self.update_command(pos, meta)
            if improper:
                self.set(pos[0], pos[1], text=meta)
                
            
        self.enter_press_innards()
        pos = self.curr_pos
        while pos and (pos[0] in self.forbidden_columns \
            or pos[1] in self.forbidden_rows):
            self.enter_press_innards()
            
        return "break"
        
        
    def tab_press_innards(self):
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
            
    def enter_press_innards(self):
        if self.curr_pos == self.final:
            # call the psased 'final' method
            # behavior in the final cell is the same for return and tab
            self.last_command()
        elif self.curr_pos[0] == int(self['width']) - 1:
            # loop to the start of the next row
            self.curr_pos = (self.start[0], self.curr_pos[1] + 1)
        else:
            # not at the end of the grid or the ed of the row
            # just move over one column (in the same row)
            self.curr_pos = (self.curr_pos[0] + 1, self.curr_pos[1])
            
        if self.curr_pos:
            self.set_curr_cell()
            
    def set_curr_cell(self):
        self.anchor_set(self.curr_pos[0], self.curr_pos[1])
        self.edit_set(self.curr_pos[0], self.curr_pos[1])
 
        
class MetaEntry():

    def __init__(self, tracks, master=None):
        """
        :param release: Current release metadata
        :param track_meta: Current track metadata
                           Dictionary of track filename -> (tag name-> tag)
        """
        tk.TopLevel.__init__(self)
        self.title("Metadata Entry Friend")
        self.tracks = tracks
        self.release = {key: value for key, value in tracks[0] if value.release}

        self.release_update = dict.fromkeys(self.release_meta.keys(), None)
        self.track_update = {}
        for key, val in self.track_meta.items():
            self.track_update[key] = dict.fromkeys(val, None)

        # set up grid for the release metadata
        self.release_grid = MetaGrid(update_command=self.update_release, last_command=self.release_end,
                                     start_index=(0, 1), forbidden_rows = [0], forbidden_columns=[],
                                     master=self, name="release_grid", width=len(self.release),
                                     height=2, selectunit="cell")

        for item in self.release:
            col =

        for item in release_categories:
            col = release_categories.index(item)
            if item == "album_artist":
                self.release_grid.size_column(index=col, size=200)
            elif item == "name":
                self.release_grid.size_column(index=col, size=250)
            else:
                self.release_grid.size_column(index=col, size=75)
                
            self.release_grid.size_column(index=col, pad0=5, pad1=5)
            
            self.release_grid.set(col, 0, text=release_mapping[item])
            
            if item in release_meta.keys():
                self.release_grid.set(col, 1, text=(str(release_meta[item])))
            else:
                self.release_grid.set(col, 1, text=str(""))
            
        # set up the track grid
        self.track_grid = MetaGrid(update_command=self.update_track, last_command=self.track_end,
                                    start_index=(1,1), forbidden_rows = [0], forbidden_columns = [0, 3], 
                                    master=master, name="track_grid", width=len(track_categories), 
                                    height=len(self.track_meta), selectunit="cell")
        
        for item in track_categories:
            col = track_categories.index(item)
            if item == "name":
                self.track_grid.size_column(index=col, size=250)
            elif item == "artist":
                self.track_grid.size_column(index=col, size=200)
            elif item == "KEXPFCCOBSCENITYRATING":
                self.track_grid.size_column(index=col, size=150)
            else:
                self.track_grid.size_column(index=col, size=75)
        
            self.track_grid.size_column(index=col, pad0=5, pad1=5)
            
            self.track_grid.set(col, 0, text=track_mapping[item])
                        
        row = 1
        for track in self.tracks:
            col = 0
            for item in track_categories:
                if item in self.track_meta[track].keys():
                    info = str(self.track_meta[track][item])
                else:
                    info = ""
                    
                self.track_grid.set(col, row, text=info)
                col += 1
            row += 1            
            
            
        l = tk.Label(master, name="track_label", text="Track Metadata")
        
        self.release_grid.pack()
        l.pack()
        self.track_grid.pack()
        self.release_grid.after(10, func=self.startup)
        
        
    def track_end(self):
        # right now we're just looping, but should move down to the 'save and quit' button in reality
        self.track_grid.curr_pos = None
        self.release_grid.curr_pos = self.release_grid.start
        self.release_grid.anchor_set(self.release_grid.curr_pos[0], self.release_grid.curr_pos[1])
        self.release_grid.edit_set(self.release_grid.curr_pos[0], self.release_grid.curr_pos[1])
        
    def release_end(self):
        # called when tab / return is pressed in the last cell of the release meta grid
        self.release_grid.curr_pos = None
        self.track_grid.curr_pos = self.track_grid.start
        self.track_grid.anchor_set(self.track_grid.curr_pos[0], self.track_grid.curr_pos[1])
        self.track_grid.edit_set(self.track_grid.curr_pos[0], self.track_grid.curr_pos[1])
        
    def startup(self):
        self.release_grid.anchor_set(self.release_grid.start[0], self.release_grid.start[1])
        self.release_grid.edit_set(self.release_grid.start[0], self.release_grid.start[1])
        
    def update_release(self, index, meta):
        """
        Update release metadata to reflect user input
        
        :param index: Int (x, y) of grid location
        :param meta: User input metadata (as a string)
        """
        if index[0] < len(release_categories) and meta > "":
        
            key = release_categories[index[0]]
            
            # check if meta has actually changed
            if self.release_update[key] is not None:
                old_meta = self.track_update[track][key]
            else:
                old_meta = self.release_meta[key]

                if str(old_meta) != meta:
                    # make sure ints remain ints
                    if type(old_meta) is int:
                        try:
                            meta = int(meta)
                            self.release_update[key] = meta
                        except ValueError:
                            # if the new meta was not an int, but the old meta was,
                            # assume there is a mistake with the new meta and toss it out
                            return old_meta
                    else:
                        self.release_update[key] = meta

        
    def update_track(self, index, meta):
        """
        Update track metadata to reflect user input
        
        :param index: Int (x, y) of track grid location
        :param meta: User input metadata (as a string)
        """
        if index[0] < len(track_categories) and index[1] < len(self.tracks):
        
            key = track_categories[index[0]]
            track = self.tracks[index[1]]
            
            # check if meta has actually changed
            if self.track_update[track][key] is not None:
                old_meta = self.track_update[track][key]
            else:
                old_meta = self.track_meta[track][key]
            
            if str(old_meta) != meta:
                # make sure ints remain ints
                if type(old_meta) is int:
                    try:
                        meta = int(meta)
                        self.track_update[track][key] = meta
                    except ValueError:
                        # If old meta is int but new meta is not
                        # Assume there is a problem with the new meta and toss it out
                        # Should probably have an obvious visual cue to demonstrate this?
                        return old_meta
                else:
                    self.track_update[track][key] = meta
                    
        print(self.track_update)
    
#    def save(self):
    

        
def main():
    root_dir = "C:\code\Meta Reviewer Tests\Files"
    meta_model = MetaModel.process_directory(root_dir)
    
    if meta_model.has_next():
        releases, tracks = meta_model.get_next_meta()
        for directory, release_meta in releases.items():
            directory = directory
            release_meta = release_meta
    
    r = tk.Tk()
    enter_meta = MetaEntry(release_meta, tracks, master=r)
    r.mainloop()
    
if __name__ == "__main__":
    main()