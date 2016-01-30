import tkinter.tix as tk
from Util import *

class MetaGrid(tk.Grid):

    def __init__(self, *args, **kwargs):
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.grid_rowconfigure(0, minsize=150, weight=200, pad=5)
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        print((x, y))
        return True
        
        
class MetaEntry(tk.Toplevel):
    def __init__(self, release_meta, track_meta, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.release_meta = release_meta
        self.track_meta = track_meta
        
        release_grid = MetaGrid(r, name="release_grid", width=500, selectunit="cell")

        for key in release_categories:
            if key in release_meta.keys():
                meta = str(release_meta[key])
            else:
                meta = ""
            index = release_categories.index(key)
            release_grid.set(index, 0, meta)