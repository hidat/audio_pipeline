import tkinter as tk
from Util import *

def display_metadata(release, tracks):
    # takes a list of release metadata
    # and a list of track metadata
    # and displays it on the screen
    
    release_str = ""
    release_values = ""
    for key, value in release.items():
        release_str += str(key) + "\t"
        release_values += str(value) + "\t"
        
    track_str = "\t"
    names = True
    track_keys = set([])
    track_values = []
    for track in tracks.values():
        track_info = "\t"
        for key, value in track.items():
            track_keys.add(key)
            if names:
                track_str += str(key) + "\t"
            track_info += str(value) + "\t"
                
        if names:
            names = False
        track_values.append(track_info)
        
    print(release_str)
    print(release_values)
    print(track_str)
    for value in track_values:
        print(value)
    
class MetaFrame(tk.Frame):

    def __init__(self, release_info, track_info, master=None):
        tk.Frame.__init__(self, master)
               
        self.release_frame = tk.Frame(self)
        release_labels = {}
        for value in release_categories.values():
            value = str(value)
            release_labels[value] = tk.Label(self.release_frame, text=value, anchor="ne")
            release_labels[value].pack(side="left", padx = 20)

            
        self.track_frame = tk.Frame(self)
        col = 2
        track_labels = {}
        for value in track_categories.values():
            value = str(value)
            track_labels[value] = tk.Label(self.track_frame, text=value, anchor="ne")
            track_labels[value].pack(side="left", padx = 20)
        
        self.release_frame.pack(padx=10, pady=5)
        self.track_frame.pack(padx=10, pady=5)
        
        self.pack()
        
    def update_release(self, release_info):
    
        release_display = {}
        col = 1
        for value in release_info:
            value = str(value) + "\t"
            release_display[value] = tk.Label(self.release_frame, text=value)
            release_display[value].grid(row=2, column=col)
            col += 1
            
        