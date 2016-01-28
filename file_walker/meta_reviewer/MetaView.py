import tkinter as tk
import tkinter.filedialog as filedialog
from Util import *

bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
heading = ('Helvetica', '10', 'bold')
standard = ('Ariel', '10')

initial_size = (500, 500)


class AppFrame(tk.Frame):


    def __init__(self, input_processor, directory_selector, background="black", master=None):
        if not master:
            master = tk.Tk()
        global bg_color
        bg_color = background
        self.body_display = None
        self.info_frame = None
        self.info_popup = None
        
        self.input_processor = input_processor
        self.directory_selector = directory_selector
        
        self.meta_location = (1, 1)
        self.input_location = (1, 2)
    
        tk.Frame.__init__(self, master, bg=bg_color, width=initial_size[0], height=initial_size[1])
        self.master["bg"] = bg_color
        
        self.menubar = tk.Menu(self)
        self.menubar.add_command(label="Change Directory", command=self.choose_dir)
        self.menubar.add_command(label="Help", command=lambda: self.display_info(commands_list, example_list))
        
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        self.master.config(menu=self.menubar)

        self.input_frame = InputFrame(master=self)
        self.input_frame.grid(row=self.input_location[1], column=self.input_location[0])
        
        self.allow_input()
        self.grid()

    def choose_dir(self):
        """
        Choose a directory containing release directories to display metadata from
        """
        choose_dir(self.directory_selector)
        
    def display_meta(self, release_info, track_info):
        """
        Display the current album's metadata
        """
        if self.body_display:
            self.body_display.close_frame()
            self.body_display = None
        
        self.body_display = MetaFrame(release_info, track_info, self)
        self.body_display.grid(row=self.meta_location[1], column=self.meta_location[0])
        
    #####
    # HELP / INFORMATION DISPLAY COMMANDS
    #####
        
    def display_info(self, command_list, display_list):
        """
        Open a new window to display metadata about 
        """
        if self.info_popup:
            self.info_popup.focus_set()
        else:
            self.info_popup = tk.Toplevel(bg=bg_color)
            self.info_popup.title("Help")
            self.info_frame = InfoFrame(self.cancel_info, master=self.info_popup)
            self.info_frame.display_commands(command_list, display_list)
                    
    def update_track(self, name, new_meta):
        self.body_display.update_track(name, new_meta)        
        
    def quit_command(self, option="Quit?"):
        self.input_frame.labeled(options=option)
        
    def clear_label(self):
        self.input_frame.clear_label()
        
    #####
    # INPUT CONTROL METHODS
    #####
    def allow_input(self):
        self.input_frame.input_entry(self.input_processor)
        
    def clear_input(self):
        self.input_frame.clear_input()
        
    def select_input(self):
        self.input_frame.select_input()
        
    def get_input(self):
        if self.input_frame.entrybox is not None:
            contents = self.input_frame.input_value.get()
        return contents
        
        
    #####
    # UTILITY FUNCTIONS
    #####
    
    def cancel_info(self):
        """
        Cleanly close the help popup, so that it can be reopened properly
        """
        self.info_popup.destroy()
        self.info_popup = None


class InfoFrame(tk.Frame):
    # the information frame should open in a new window, because some people might want to reference it?
    
    def __init__(self, close_command, master=None):
        tk.Frame.__init__(self, master, bg=bg_color)
        self.master.protocol("WM_DELETE_WINDOW", close_command)
        self.grid()
        
    def display_commands(self, command_list, example_list):
        """
        Displays a passed dictionary of command -> command effects onscreen
        """
        row_index = 0
        col_index = 0
        
        description_label = tk.Label(self, text="Commands", bg=bg_color, fg=text_color, anchor="nw", font=heading)
        description_label.grid(row=row_index, column=col_index, padx=5, pady=3)
        
        row_index += 1
        col_index += 1
                        
        for command, description in command_list.items():
            comm = tk.Label(self, text=command, bg=bg_color, fg=text_color, anchor="nw", font=heading)
            desc = tk.Label(self, text=description, bg=bg_color, fg=text_color, anchor="nw")
            comm.grid(row=row_index, column=col_index, sticky="w", padx=5, pady=3)
            col_index += 1
            desc.grid(row=row_index, column=col_index, sticky="w", padx=5, pady=3)
            row_index += 1
            if command in example_list.keys():
                example_title = tk.Label(self, text="Example:", bg=bg_color, fg=text_color, anchor="nw", font=heading)
                example_title.grid(row=row_index, column=col_index, sticky="w", padx=2, pady=1)
                row_index += 1
                example = tk.Label(self, text="\t" + example_list[command], bg=bg_color, fg=text_color, anchor="nw")
                example.grid(row=row_index, column=col_index, sticky="w", padx=2, pady=2)
                row_index += 1
            col_index = 1
            
    def cancel(self):
        if master:
            self.master.focus_set()
        self.destroy()
        return None    


class InputFrame(tk.Frame):

    def __init__(self, master=None):
        self.entrybox = None
        self.label = None
    
        tk.Frame.__init__(self, master, bg=bg_color)
        self.grid()
        
        
    def input_entry(self, input_processor):
        # use an entry box to get user input        
        self.entrybox = tk.Entry(self, exportselection=0)
        self.entrybox.grid()
        
        self.input_value = tk.StringVar()
        self.input_value.set("Input input here")
        self.entrybox['textvariable'] = self.input_value
        self.entrybox.focus_set()
        self.entrybox.select_range(0, tk.END)
        
        self.entrybox.bind('<Key-Return>', input_processor)
        
    def select_input(self):
        if self.entrybox:
            self.entrybox.select_range(0, tk.END)
        
    def clear_input(self):
        if self.entrybox:
            self.entrybox.delete(0, tk.END)
    
    def labeled(self, options):
        self.label = tk.Label(self, bg=bg_color, fg=text_color, text=options)
        self.label.grid(row=0, column=0)
       
    def clear_label(self):
        if self.label:
            self.label.destroy()
        
    def close_frame(self):
        self.destroy()
        
        
class MetaFrame(tk.Frame):

    def __init__(self, release_info, track_info, master=None):
        tk.Frame.__init__(self, master, bg=bg_color)

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

    def update_track(self, name, meta):
        for key in track_categories:
            value=""
            if key in meta.keys():
                value = str(meta[key])
                self.track_attributes[name][key].config(text=value)
            elif key in self.track_attributes[name].keys():
                self.track_attributes[name][key].config(text="")
            if "KEXPFCCOBSCENITYRATING" in meta.keys():
                obscenity = meta["KEXPFCCOBSCENITYRATING"].casefold()
                if obscenity == "yellow dot":
                    color = yellow
                elif obscenity == "red dot":
                    color = red
                self.track_attributes[name][key].config(fg=color)
            else:
                self.track_attributes[name][key].config(fg=text_color)
                
    def close_frame(self):
        self.destroy()
        
class DialogBox(tk.Toplevel):

    def __init__(self, message, buttons=None, dimensions=(100,75), cancel=False, title=None, master=None):
        """
        Create a dialog popup box containing the specified message string and button options.
        
        :param message: string message to display in popup
        :param buttons: List of button directories; each button directory must contain
                        {"name": name, "command": command}
        """
        tk.Toplevel.__init__(self, master, width=dimensions[0], height=dimensions[1])
        if master:
            self.master = master
            self.transient(master)
            location = "+" + str(self.master.winfo_rootx() + 50) +\
                       "+" + str(self.master.winfo_rooty() + 50)
            self.geometry(location)
            
        if title:
            self.title(title)
            
        self.text(message)
        if buttons:
            self.button_box(buttons)
            
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
    def text(self, message):
        label = tk.Label(self, text=message)
        label.pack()
        
    def button_box(self, buttons):
        box = tk.Frame(self)
        
        for i in range(0, len(buttons)):
            button = buttons[i]
            if not "command" in button.keys() or not button["command"]:
                button["command"] = self.cancel
            but = tk.Button(box, text=button["name"], command=lambda x=button["command"]: self.apply(x))
            if i == 0:
                but.focus_set()
                
            but.bind("<Return>", but['command'])
            but.pack(side=tk.LEFT, padx=5,pady=5)

        box.pack()
        self.wait_window(self)
    
    def apply(self, command):
        self.cancel()
        command()

    def cancel(self):
        self.destroy()
        
def choose_dir(directory_selector, master=None, initial_dir="\\", withdraw=True):
    if withdraw:
        tk.Tk().withdraw()
    directory_name = filedialog.askdirectory(title="fialog", parent=master, initialdir=initial_dir, mustexist=True)
    # if
    directory_selector(directory_name)
    
    
def err_message(message, ok_command, parent=None, quit=False):
    err_display = DialogBox(message, master=parent)
    buttons = [{"name": "OK", "command": ok_command}]
    if quit:
        buttons.append({"name": "Quit", "command": err_display.cancel})
    err_display.button_box(buttons)