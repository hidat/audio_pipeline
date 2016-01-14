import tkinter as tk
from Util import *

bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
heading = ('Helvetica', '10', 'bold')
standard = ('Ariel', '10')

class AppFrame(tk.Frame):

    def __init__(self, input_processor, background="black", master=None):
        self.meta_display = None
        self.button = None
        
        self.meta_location = (1, 1)
        self.input_location = (2, 1)
    
        global bg_color
        bg_color = "black"
        tk.Frame.__init__(self, master, bg=bg_color)

        self.input_frame = InputFrame(master=self)
        self.input_frame.grid(row=self.input_location[0], column=self.input_location[1])
        
        self.grid()

    def display_meta(self, release_info, track_info):
        if self.meta_display is not None:
            self.meta_display.quit()
        
        self.meta_display = MetaFrame(release_info, track_info, self)
        self.meta_display.grid(row=self.meta_location[0], column=self.meta_location[1])
        
    def allow_input(self, input_processor):
        self.input_frame.input_entry(input_processor)
        
    def clear_input(self):
        self.input_frame.clear_input()
        
    def complete_button(self, option="Quit?"):
        self.input_frame.button(options=option)
        
    def get_input(self):
        if self.input_frame.entrybox is not None:
            contents = self.input_frame.input_value.get()
        return contents
        
    def quit(self):
        self.master.destroy()

       
class InputFrame(tk.Frame):

    def __init__(self, master=None):
        self.entrybox = None
        self.complete_button = None
    
        tk.Frame.__init__(self, master, bg=bg_color)
        self.grid()
        
    def input_entry(self, input_processor):
        # use an entry box to get user input
        if self.complete_button is not None:
            self.complete_button.destroy()
        
        self.entrybox = tk.Entry(self, exportselection=0)
        self.entrybox.grid()
        
        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.entrybox['textvariable'] = self.input_value
        self.entrybox.focus_set()
        self.entrybox.select_range(0, tk.END)
        
        self.entrybox.bind('<Key-Return>', input_processor)
        
    def clear_input(self):
        if self.entrybox is not None:
            self.entrybox.delete(0, tk.END)
          
    def button(self, options="Quit?"):
        if self.entrybox is not None:
            self.entrybox.destroy()
        self.complete_button = tk.Button(self, text=options, command=self.quit_all)
        self.complete_button.grid()
        
        self.complete_button.bind('<Key-Return>', self.complete_button['command'])
        self.complete_button.focus_set()
    
    def quit(self):
        self.destroy()
        
    def quit_all(self):
        self.master.quit()
        
class EntryFrame(tk.Frame):
    # Frame that keeps track of the input
    def __init__(self, input_processor, master=None):
        tk.Frame.__init__(self, master, bg=bg_color)

        self.input = tk.Entry(self, exportselection=0)
        self.input.grid()

        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.input["textvariable"] = self.input_value
        self.input.focus_set()
        self.input.select_range(0, tk.END)

        self.input.bind('<Key-Return>', input_processor)
        
    def clear_input(self):
        self.input.delete(0, tk.END)
        
    def quit(self):
        self.destroy()

        
class OptionsFrame(tk.Frame):
    # Frame with a 'quit' button
    def __init__(self, options="Quit?", master=None):
        tk.Frame.__init__(self, master, bg=bg_color)
        
        self.complete_button = tk.Button(self, text=options, command=self.quit_all)
        
        self.complete_button.grid()
        
    def quit(self):
        self.destroy()
        
    def quit_all(self):
        self.master.quit()

class MetaFrame(tk.Frame):

    def __init__(self, release_info, track_info, master=None):
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
            
    def quit(self):
        self.destroy()

    def really_quit(self):
        self.master.quit()
