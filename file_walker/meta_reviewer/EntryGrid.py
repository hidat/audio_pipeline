import tkinter.tix as tk
from Util import *

class MetaGrid(tk.Grid):

    def __init__(self, *args, **kwargs):
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        print((x, y))
        return True
        
r = tk.Tk()
r.title("MetaReviewer")

l = tk.Label(r, name="a_label")
l.pack()

g = MetaGrid(r, name="metadata_grid", selectunit="cell")
g.pack(fill=tk.BOTH)

x = 0
y = 0
for attribute in track_categories:
    g.set(x,y,text=str(track_mapping[attribute]))
    x += 1
    
print(g.entrycget(0,0))
        
c = tk.Button(r, text="Close", command=r.destroy)
c.pack()

tk.mainloop()