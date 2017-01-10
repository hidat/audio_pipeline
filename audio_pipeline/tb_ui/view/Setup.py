import tkinter.tix as tk
from .. import min_width, min_height, Command, release_tags, track_tags
from . import Settings
import copy
from collections import OrderedDict

setup_release_tags = release_tags[:] #[tag.copy() for tag in release_tags]
setup_track_tags = track_tags[:] #[tag.copy() for tag in track_tags]

class App(tk.Toplevel):
    
    def __init__(self):
        global setup_release_tags, setup_track_tags
        setup_release_tags = [copy.deepcopy(tag) for tag in release_tags]
        setup_track_tags = [copy.deepcopy(tag) for tag in track_tags]
        tk.Toplevel.__init__(self)
                
        self.setup_options = OrderedDict()
        
        width_frame = tk.Frame(master=self, width=min_width, height=0)
        width_frame.grid(row=0, column=1, sticky="nw")
        height_frame = tk.Frame(master=self, height=min_height, width=0)
        height_frame.grid(row=1, column=0, sticky="nw")

        self.content_frame = tk.Frame(master=self)

        self.setup_options["tag_name"] = tk.Label(master=self.content_frame, text="Tag Name", font=Settings.heading)
        self.setup_options["display_name"] = tk.Label(master=self.content_frame, text="Display Name", font=Settings.heading)
        self.setup_options["aliases"] = tk.Label(master=self.content_frame, text="Aliases", font=Settings.heading)
        self.setup_options["options"] = tk.Label(master=self.content_frame, text="Options", font=Settings.heading)
        self.setup_options["tag_level"] = tk.Label(master=self.content_frame, text="Command Level", font=Settings.heading)
        self.setup_options["active"] = tk.Label(master=self.content_frame, text="Active", font=Settings.heading)
        self.setup_options["freeform"] = tk.Label(master=self.content_frame, text="Freeform Tag", font=Settings.heading)
        self.setup_options["help"] = tk.Label(master=self.content_frame, text="Command Help", font=Settings.heading)
        
        column_val = 0
        row_val = 0
        for setup_option in self.setup_options.values():
            setup_option.grid(row=row_val, column=column_val, sticky="nw", pady=3, padx=10)
            column_val += 1
            
        row_val += 1
        column_val = list(self.setup_options.keys()).index("options")
        options_header = OptionsHeader(self.content_frame)
        options_header.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
        print(column_val)
        print(row_val)
        self.tag_levels = {}
        row_val += 1
        for tag in setup_track_tags + setup_release_tags:
            column_val = list(self.setup_options.keys()).index("tag_name") 
            name_tag = NameTag(self.content_frame, tag)
            name_tag.tag_entry.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
            
            column_val = list(self.setup_options.keys()).index("display_name") 
            name_tag.display_entry.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
            
            column_val = list(self.setup_options.keys()).index("aliases")
            aliases = Aliases(self.content_frame, tag.aliases, tag)
            aliases.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")

            column_val = list(self.setup_options.keys()).index("tag_level") 
            tag_level = TagLevel(self.content_frame, tag, row_val)
            tag_level.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
            
            column_val = list(self.setup_options.keys()).index("active") 
            active = ActiveCommand(self.content_frame, tag)
            active.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
            
            column_val = list(self.setup_options.keys()).index("freeform")
            freeform = FreeformTag(self.content_frame, tag)
            freeform.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")
            
            column_val = list(self.setup_options.keys()).index("options")
            options = OptionsList(self.content_frame, tag)
            options.grid(column=column_val, row=row_val, pady=3, padx=3, sticky="n")

            row_val += 1
            
        self.content_frame.grid(row=1, column=1, sticky="nw")
        
        self.save_button = tk.Button(self, text="Save", command=self.save_changes)
        
        self.grid()
        
    def complete(self):
        self.save()
        
    def save_changes(self):
        global setup_release_tags, setup_track_tags
        release_tags = setup_release_tags
        track_tags = setup_track_tags
        

class NameTag():
    
    def __init__(self, master, command):
        self.command = command
        self.tag = tk.StringVar()
        self.tag.set(self.command.command)
        self.display = tk.StringVar()
        self.display.set(self.command.display_name)
        self.display.trace("w", self.display_set)
        self.tag_entry = tk.Entry(master, textvar=self.tag, exportselection=False)
        self.display_entry = tk.Entry(master, textvar=self.display, exportselection=False)

        self.tag_entry.bind("<Return>", self.process_tag_input)
        self.display_entry.bind("<Return>", self.process_display_input)
        
    def process_tag_input(self, *args):
        selection = self.tag.get()
        if self.command.command == self.command.display_name:
            self.display.set(selection)
        self.command.command = selection
        
    def process_display_input(self, *args):
        selection = self.display.get()
        print(selection)

    def display_set(self, *args):
        self.command.display_name = self.display.get()
        print("we've changed the text variable!")
        print(self.display.get())

        
class ActiveCommand(tk.Frame):
    
    def __init__(self, master, command):
        tk.Frame.__init__(self, master)
        self.command = command
        self.var = tk.BooleanVar()
        self.var.set(self.command.active)
        self.active = tk.Checkbutton(self, variable=self.var, onvalue=True, offvalue=False)
        self.active.grid()
    
    def toggle(self):
        self.command.active = self.var.get()
        
class FreeformTag(ActiveCommand):
    
    def __init__(self, *args):
        super().__init__(*args)
        self.var.set(self.command.freeform)
        
    def toggle(self):
        self.command.active = self.var.get()
        
class TagLevel(tk.Frame):
    
    def __init__(self, master, command, command_index):
        self.command_index = command_index
        self.command = command
        self.var = tk.BooleanVar()
        self.var.set(command.track)
        self.var.trace("w", self.change_tag_level)
        tk.Frame.__init__(self, master)
        self.track = tk.Radiobutton(self, text="Track", variable=self.var, value=True)
        self.track.grid(row=0, column=0, pady=1, padx=3, sticky="nw")
        self.release = tk.Radiobutton(self, text="Release", variable=self.var, value=False)
        self.release.grid(row=1, column=0, pady=1, padx=3, sticky="nw")
        
        
    def change_tag_level(self, *args):
        val = self.var.get()
                
        if self.command.track != val:
            self.command.track = val
            global setup_track_tags, setup_release_tags
            if val == True:
                setup_track_tags.append(self.command)
                setup_release_tags.remove(self.command)
                self.track.select()
                self.release.deselect()
            else:
                setup_release_tags.append(self.command)
                setup_track_tags.remove(self.command)
                self.release.select()
                self.track.deselect()
            print(track_tags)
            print(release_tags)
            
class OptionsHeader(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tag_value = tk.Label(self, text="Tag Value")
        entry_options = tk.Label(self, text="Valid TB entry to set tag value")
        tag_value.grid(row=0, column=0, padx=3, pady=3)
        entry_options.grid(row=0, column=1, padx=3, pady=3)

                
class OptionsList(tk.Frame):
    
    def __init__(self, master, command):
        tk.Frame.__init__(self, master)
        row_val = 0
        self.options = {}
        for option in command.options:
            opt = HiddenEntry(self, option.command)
            opt.grid(row=row_val, column=0)
            
            aliases = Aliases(self, [option.alias])
            aliases.grid(row=row_val, column=1)
            self.options[option.command] = (opt, aliases)
            row_val += 1
        self.extra_option = HiddenEntry(self, " ")
        self.extra_option.grid(row=row_val, column=0)
        self.extra_aliases = Aliases(self, " ")
        self.extra_aliases.grid(row=row_val, column=1)      
          
class HiddenEntry(tk.Entry):
    
    def __init__(self, master, starting_contents):
        self.val = tk.StringVar()
        self.val.set(starting_contents)
        self.master = master
        
        tk.Entry.__init__(self, master, state="readonly", textvariable=self.val, relief="groove")

        self.can_edit = False
        self.bind("<Enter>", self.selection_possible)
        self.bind("<Leave>", self.end_possible_selection)
        self.bind("<FocusIn>", self.full_selection)
        self.bind("<FocusOut>", self.remove_focus)
        
        self.bind("<Button-1>", self.do_selection)
        
    def selection_possible(self, *args):
        self.can_edit = True
        
    def remove_focus(self, *args):
        if self.can_edit:
            current_val = self.val.get()
            
        self.end_possible_selection()
        self["state"] = "readonly"
        
    def end_possible_selection(self, *args):
        self.can_edit = False
        
    def full_selection(self, *args):
        self.can_edit = True
        self.do_selection()

    def do_selection(self, *args):
        if self.can_edit:
            self["state"] = "normal"
            self.focus_set()
            self.select_range(0, tk.END)
            
class Aliases(HiddenEntry):
    
    def __init__(self, master, alias_list, command=None):
        aliases = ", ".join(alias_list)
        self.command = command
        super().__init__(master, aliases)

    def process_aliases(self):
        aliases = self.val.get()
        alias_list = [alias.strip() for alias in aliases.split(",")]
        
        return alias_list
        