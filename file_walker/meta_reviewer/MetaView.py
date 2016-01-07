import tkinter as tk
from Util import *

class MetaFrame(tk.Frame):

    def __init__(self, release_info, track_info, master=None):
        tk.Frame.__init__(self, master, bg="black")
        
        self.release_frame = tk.Frame(self, bg="black")
        self.release_attribute_frames = []
        for value in release_categories:
            value = str(value)
            self.release_attribute_frames.append(tk.Frame(self.release_frame, bg="black"))
            
        self.current_tracks = {}
            
        self.track_frame = tk.Frame(self, bg="black")
        self.track_attribute_frames = []
        for value in track_categories:
            value = str(value)
            self.track_attribute_frames.append(tk.Frame(self.track_frame, bg="black"))

        self.track_display = {}
        self.update_tracks(track_info)
        self.update_release(release_info)
        
        self.release_frame.pack(padx=10, pady=5)
        for frame in self.release_attribute_frames:
            frame.pack(side="left", padx=20)
        for frame in self.track_attribute_frames:
            frame.pack(side="left", padx=20)
        self.track_frame.pack(padx=10, pady=5)

        self.input_frame = tk.Frame(self)
        self.input = tk.Entry(self.input_frame, exportselection=0)
        self.input.pack()

        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.input["textvariable"] = self.input_value
        self.input.focus_set()
        self.input.select_range(0, tk.END)

        #self.input.bind('<Key-Return>', MetaControl.MetaCotroller.process_contents)
        
        self.input_frame.pack(pady=5)
        
        self.pack()

    def yellow(self, name):
        if name in self.track_display.keys():
            for label in self.track_display[name].values():
                label.config(fg='yellow')
        
    def red(self, name):
        if name in self.track_display.keys():
            print(name)
            for label in self.track_display[name].values():
                label.config(fg='red')
        

    def clear_input(self):
        self.input.select_range(0, tk.END)
        #self.input.delete(0, tk.END)
        
    def update_release(self, release_info):
    
        release_display = {}
        for key, value in release_info.items():
            key = str(key)
            if key in release_categories:
                value = str(value)
                index = release_categories.index(key)
                release_display[key] = tk.Label(self.release_attribute_frames[index], text=value,
                                                 anchor="nw", bg="black", fg="white")
                release_display[key].pack(side="top")
            
    def update_tracks(self, track_info):
        self.current_tracks.clear()
        self.track_display.clear()
        
        frame_widths = {}
        keys = track_info.keys()
        keys = list(keys)
        keys.sort()

        for name in keys:
            track = track_info[name]
            self.current_tracks[track["track_num"]] = name
            self.track_display[name] = {}

            color = "light gray"
            if "KEXPFCCOBSCENITYRATING" in track.keys():
                obscenity = track["KEXPFCCOBSCENITYRATING"].casefold()
                if obscenity == "yellow dot":
                    color = "yellow"
                elif obscenity == "red dot":
                    color = "red"

            for key in track_categories:
                if key not in frame_widths.keys():
                    frame_widths[key] = 0
                value = ""
                index = track_categories.index(key)
                if key in track.keys():
                    value = str(track[key])
                    frame_widths[key] = max(frame_widths[key], len(value))
                        
                self.track_display[name][key] = tk.Label(self.track_attribute_frames[index],
                                                             text=value, anchor="nw", fg=color, bg="black")


        for name in keys:
            track = self.track_display[name]
            for attribute, label in track.items():
                print(attribute)
                label.config(width=frame_widths[attribute])
                label.pack(side="top")
                
    def quit(self):
        self.destroy()
