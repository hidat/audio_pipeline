import tkinter as tk
from Util import *

bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
heading = ('Helvetica', '10', 'bold')
standard = ('Ariel', '10')

class MetaFrame(tk.Frame):

    def __init__(self, input_processor, release_info, track_info, background="black", master=None):
        global bg_color
        bg_color = background
        tk.Frame.__init__(self, master, bg=bg_color)

        self.current_tracks = {}

        self.release_frame = tk.Frame(self, bg=bg_color)
        self.track_frame = tk.Frame(self, bg=bg_color)
        self.input_frame = tk.Frame(self, bg=bg_color)
        
        self.release_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.track_frame.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.input_frame.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        release_attribute_labels = []
        self.release_attributes = {}
        colval = 0
        for value in release_categories:
            index = release_categories.index(value)
            value = str(value)
            release_attribute_label = tk.Label(self.release_frame, fg=text_color, font=heading, 
                                                 bg=bg_color, text=release_mapping[value])
            release_attribute_labels.append(release_attribute_label)
            release_attribute_labels[index].grid(row=0, column=colval, sticky="w", padx=10, pady=5)
            colval += 1

        self.display_release(release_info)

        track_attribute_labels = []
        self.track_attributes = {}
        colval = 1
        for value in track_categories:
            index = track_categories.index(value)
            value = str(value)
            track_attribute_label = tk.Label(self.track_frame, fg=text_color, font=heading, 
                                             bg=bg_color, text=track_mapping[value])
            track_attribute_labels.append(track_attribute_label)
            track_attribute_labels[index].grid(row=0, column=colval, sticky="w", padx=10, pady=5)
            colval += 1

        self.display_tracks(track_info)

        self.input = tk.Entry(self.input_frame, exportselection=0)
        self.input.grid()

        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.input["textvariable"] = self.input_value
        self.input.focus_set()
        self.input.select_range(0, tk.END)

        self.input.bind('<Key-Return>', input_processor)

        self.grid()

    def display_release(self, release_info):
        rowval = 1
        colval = 0
        for key in release_categories:
            if key in release_info.keys():
                value = str(release_info[key])
            else:
                value = ""
            index = release_categories.index(key)
            self.release_attributes[key] = tk.Label(self.release_frame, text=value, anchor="nw",
                                                    bg=bg_color, fg=text_color)
            self.release_attributes[key].grid(row=rowval, column=colval, sticky="w", padx=10, pady=5)
            colval += 1

    def display_tracks(self, track_info):
        self.current_tracks.clear()
        self.track_attributes.clear()

        padding_label = tk.Label(self.track_frame, text="        ", bg=bg_color)
        padding_label.grid(row=0, column=0)

        keys = track_info.keys()
        keys = list(keys)
        keys.sort()

        rowval = 1
        colval = 1
        for name in keys:
            track = track_info[name]
            self.current_tracks[track["track_num"]] = name
            self.track_attributes[name] = {}

            color = text_color
            if "KEXPFCCOBSCENITYRATING" in track.keys():
                obscenity = track["KEXPFCCOBSCENITYRATING"].casefold()
                if obscenity == "yellow dot":
                    color = yellow
                elif obscenity == "red dot":
                    color = red

            for key in track_categories:
                value = ""
                index = track_categories.index(key)
                if key in track.keys():
                    value = str(track[key])
                self.track_attributes[name][key] = tk.Label(self.track_frame, text=value, anchor="nw", fg=color, bg=bg_color)
                self.track_attributes[name][key].grid(row=rowval, column=colval, sticky="w", padx=10, pady=5)
                colval += 1
            rowval += 1
            colval = 1

    def update_track(self, name, new_meta):
        for key in track_categories:
            value=""
            if key in new_meta.keys():
                value = str(new_meta[key])
                self.track_attributes[name][key].config(text=value)
            if "KEXPFCCOBSCENITYRATING" in new_meta.keys():
                obscenity = new_meta["KEXPFCCOBSCENITYRATING"].casefold()
                if obscenity == "yellow dot":
                    color = yellow
                elif obscenity == "red dot":
                    color = red
                self.track_attributes[name][key].config(fg=color)
            
    def clear_input(self):
        self.input.delete(0, tk.END)

    def quit(self):
        self.destroy()