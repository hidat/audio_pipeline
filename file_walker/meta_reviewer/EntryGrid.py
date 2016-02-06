import tkinter.tix as tk
from Util import *
import MetaModel

class MetaGrid(tk.Grid):

    def __init__(self, *args, **kwargs):
        tk.Grid.__init__(self, *args, **kwargs)
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        print((x, y))
        return True
        
class MetaEntry():

    no_edit_row = '0'

    def __init__(self, release_meta, track_meta, master=None, *args, **kwargs):
        """
        :param release_meta: Current release metadata
        :param track_meta: Current track metadata
                           Dictionary of track filename -> (tag name-> tag)
        """
        # tk.Toplevel.__init__(self, *args, **kwargs)
        # self.title("Metadata Entry Friend")
        self.release_meta = release_meta
        self.track_meta = track_meta
        self.current_release_index = None
        self.current_track_index = None
        
        # set up the release grid
        self.release_grid = MetaGrid(master, name="release_grid", width=len(release_categories),
                                    height=2, selectunit="cell", editnotify=self.release_select)
        
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
        self.track_grid = MetaGrid(master, name="track_grid", width=len(track_categories),
                                   selectunit="cell", editnotify=self.track_select)
        
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
            
        l = tk.Label(master, name="track_label", text="Track Metadata")
        
        self.release_grid.pack()
        l.pack()
        self.track_grid.pack()
        
    def track_select(self, x, y):
        # track selection
        if self.current_release_index:
            self.current_release_index = None
        
        self.current_track_index = (x, y)
        print("track select")
        print((x, y))
        if y == self.no_edit_row:
            return False
        else:
            return True

    def release_select(self, x, y):
        # release selection
        if self.current_track_index:
            self.current_track_index = None
            
        self.current_release_selection = (x,y)
        print("release select")
        print((x, y))
        if y == self.no_edit_row:
            return False
        else:
            return True
        
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