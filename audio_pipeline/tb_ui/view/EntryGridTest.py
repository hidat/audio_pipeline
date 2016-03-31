from EntryGrid import *
import MetaModel
import tkinter.tix as tk

r = tk.Tk()
r.title("MetaReviewer")

root_dir = "C:\code\Meta Reviewer Tests\Files"
meta_model = MetaModel.process_directory(root_dir)
if meta_model.has_next():
    releases, tracks = meta_model.get_next_meta()
    for directory, release_meta in releases.items():
        directory = directory
        release_meta = release_meta
        

release_grid = MetaGrid(r, name="release_grid", width=len(release_categories), height=2, selectunit="cell")
release_grid.size_column(index=0, size=200, pad0=3, pad1=3)
release_grid.size_column(index=1, size=150, pad0=3, pad1=3)
release_grid.size_column(index=2, size=50, pad0=3, pad1=3)


for key in release_categories:
    if key in release_meta.keys():
        meta = str(release_meta[key])
    else:
        meta = ""
    index = release_categories.index(key)
    release_grid.set(index, 0, text=release_mapping[key])
    release_grid.set(index, 1, text=(meta))

    
release_grid.pack()

l = tk.Label(r, name="a_label", text="Track Metadata")
l.pack()

g = MetaGrid(r, name="metadata_grid", selectunit="cell")
g.pack(fill=tk.BOTH)

x = 0
y = 0
for attribute in track_categories:
    g.set(x,y,text=str(track_mapping[attribute]))
    g.size_column(index=x, size=100, pad0=3, pad1=3)
    x += 1

c = tk.Button(r, text="Close", command=r.destroy)
c.pack()

tk.mainloop()