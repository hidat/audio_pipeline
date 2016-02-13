import tkinter.tix as tk
from Util import *
import MetaModel

class MetaGrid(tk.Grid):

    def __init__(self, last_command, start_index, forbidden_rows, forbidden_columns, *args, **kwargs):
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.last_command = last_command
        if 'width' in kwargs and 'height' in kwargs:
            self.start =  start_index
            self.final = (int(self['width']) - 1, int(self['height']) - 1)
            
        self.forbidden_rows = forbidden_rows
        self.forbidden_columns = forbidden_columns
        self.curr_pos = self.start
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        self.bind_class("Entry", "<Tab>", self.tab_press)
        self.curr_pos = (int(x), int(y))
        if int(y) in self.forbidden_rows:
            return False
        elif int(x) in self.forbidden_columns:
            return False
        else:
            return True
            
    def tab_press(self, event):
        self.tab_press_innards()
        while self.curr_pos and (int(self.curr_pos[0]) in self.forbidden_columns \
            or int(self.curr_pos[1]) in self.forbidden_rows):
            self.tab_press_innards()
            
        return "break"
        
    def tab_press_innards(self):
        if self.curr_pos == self.final:
            # call a passed method
            self.last_command()
        elif self.curr_pos[1] == int(self['height']) - 1:
            # loop to the start of the next column
            self.curr_pos = (self.curr_pos[0] + 1, self.start[1])
            self.anchor_set(self.curr_pos[0], self.curr_pos[1])
            self.edit_set(self.curr_pos[0], self.curr_pos[1])
        else:
            # not at the end of the grid or the end of the column - just move down one row
            self.curr_pos = (self.curr_pos[0], self.curr_pos[1] + 1)
            self.anchor_set(self.curr_pos[0], self.curr_pos[1])
            self.edit_set(self.curr_pos[0], self.curr_pos[1])

            
        
class MetaEntry():

    def __init__(self, release_meta, track_meta, master=None, *args, **kwargs):
        """
        :param release_meta: Current release metadata
        :param track_meta: Current track metadata
                           Dictionary of track filename -> (tag name-> tag)
        """
        # tk.Toplevel.__init__(self, *args, **kwargs)
        # self.title("Metadata Entry Friend")
        self.release_meta = release_meta
        self.tracks = sorted(track_meta, key=lambda track: track_meta[track]['track_num'])
        self.track_meta = track_meta
        
        # set up the release grid
        self.release_grid = MetaGrid(last_command=self.release_end, start_index=(0, 1),
                                    forbidden_rows = [0], forbidden_columns=[], master=master, 
                                    name="release_grid", width=len(release_categories),
                                    height=2, selectunit="cell")
        
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
            
        # set up the track grid
        self.track_grid = MetaGrid(last_command=self.track_end, start_index=(1,1),
                                    forbidden_rows = [0], forbidden_columns = [0, 3], master=master,
                                    name="track_grid", width=len(track_categories), height=len(self.track_meta), 
                                    selectunit="cell")
        
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
    
    
main()