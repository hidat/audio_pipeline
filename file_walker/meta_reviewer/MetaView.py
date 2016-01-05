import tkinter as tk
from Util import *
import MetaModel

class MetaFrame(tk.Frame):

    def __init__(self, release_info, track_info, master=None):
        tk.Frame.__init__(self, master)
               
        self.release_frame = tk.Frame(self)
        self.release_attribute_frames = {}
        release_labels = {}
        for value in release_categories.values():
            value = str(value)
            self.release_attribute_frames[value] = tk.Frame(self.release_frame)
            release_labels[value] = tk.Label(self.release_attribute_frames[value], text=value, anchor="ne")
            release_labels[value].pack(side="top", padx=10)


        self.current_tracks = {}
            
        self.track_frame = tk.Frame(self)
        col = 2
        self.track_labels = {}
        self.track_attribute_frames = {}
        for value in track_categories.values():
            value = str(value)
            self.track_attribute_frames[value] = tk.Frame(self.track_frame)
            self.track_labels[value] = tk.Label(self.track_attribute_frames[value], text=value, anchor="sw")
            self.track_labels[value].pack(side="top", padx = 10)

        self.update_release(release_info)
        self.update_tracks(track_info)
        
        self.release_frame.pack(padx=10, pady=5)
        for frame in self.release_attribute_frames.values():
            frame.pack(side="left", padx=20)
        for frame in self.track_attribute_frames.values():
            frame.pack(side="left", padx=20)
        self.track_frame.pack(padx=10, pady=5)

        self.input_frame = tk.Frame(self)
        self.input = tk.Entry(self.input_frame)
        self.input.pack()

        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.input["textvariable"] = self.input_value

        self.input.bind('<Key-Return>', self.process_contents)
        
        self.input_frame.pack(pady=5)
        
        self.pack()

    def process_contents(self, event):
        contents = self.input_value.get().split()
        content_length = len(contents)
        if content_length == 2:
            try:
                track_num = int(contents[0])
                value = contents[1].casefold()
                if track_num not in self.current_tracks.keys():
                    print("Invalid track number")
                elif value == "y" or value == "yellow" or value == "yellow dot":
                    print(self.current_tracks[track_num])
                elif value == "r" or value == "red" or value == "red dot":
                    print(self.current_tracks[track_num])
            except: # whatever the integer failure error is
                print("Whoops haha")
            
        
    def update_release(self, release_info):
    
        release_display = {}
        for key, value in release_info.items():
            key = str(key)
            if key in release_categories:
                value = str(value)
                release_display[key] = tk.Label(self.release_attribute_frames[release_categories[key]], text=value, anchor="ne")
                release_display[key].pack(side="bottom")
            
    def update_tracks(self, track_info):
        self.current_tracks.clear()
        
        track_display = {}
        keys = track_info.keys()
        keys = list(keys)
        keys.sort()
        for name in keys:
            track = track_info[name]
            self.current_tracks[track["track_num"]] = name
            for key, value in track.items():
                key = str(key)
                if key in track_categories:
                    value = str(value)
                    if name not in track_display:
                        track_display[name] = {}
                    track_display[name][key] = tk.Label(self.track_attribute_frames[track_categories[key]],
                                                          text=value, anchor="ne")
                    track_display[name][key].pack(side="top")
