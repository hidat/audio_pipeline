from . import Settings
from .. import release_tags, track_tags, general_commands
import tkinter.tix as tk
        
        
class InfoFrame(tk.Frame):
    _command_width = 30
    _desc_width = 70
    
    def __init__(self, master=None):
        self.desc = None
        self.command_frame = None
        self.master = master
        
        width_frame = tk.Frame(master=master, bg=Settings.bg_color, width=115*8, height=0)
        width_frame.grid(row=0, column=1, padx=5, pady=3, sticky="nw")
        height_frame = tk.Frame(master=master, bg=Settings.bg_color, height=70*8, width=0)
        height_frame.grid(row=1, column=0, padx=5, pady=3, sticky="nw")

        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        menubar = tk.Menu(self.master)
        menubar.add_command(label="General Commands", command=lambda: self.display_commands(general_commands, "General Commands"))
        menubar.add_command(label="Track Commands", command=lambda: self.display_commands(track_tags, "Track Metadata"))
        menubar.add_command(label="Release Commands", command=lambda: self.display_commands(release_tags, "Release Metadata"))
        self.master.config(menu=menubar)
        self.grid(row=1, column=1, padx=5, pady=3, sticky="nw")
        self.attributes = []
        menubar.invoke(1)
        
    def clear(self):
        for label in self.attributes:
            label.destroy()


    def display_commands(self, commands, section_header):
        """
        Display information about available commands onscreen

        :return:
        """ 
        desc = tk.Label(self, text=section_header, bg=Settings.bg_color, fg=Settings.text_color,
            anchor="nw", font=Settings.heading)
        desc.grid(row=0, column=0, padx=5, pady=3, sticky="nw")
        if self.desc:
            self.desc.destroy()
            self.desc = None
        self.desc = desc
        
        if self.command_frame:
            self.command_frame.destroy()
            self.command_frame = None
        self.populate_frame(commands, 0, section_header)
            
    def populate_frame(self, commands, base_row, section_header):        
        base_row += 1
        
        self.command_frame = tk.Frame(self, bg=Settings.bg_color)
        self.command_frame.grid(row=base_row, column=0, sticky="nw")
        self.attributes.append(self.command_frame)
        
        base_row += 1
        
        rowval = 0
        colval = 0

        spacer = tk.Label(self.command_frame, text="\t\t", bg=Settings.bg_color)
        spacer.grid(row=rowval, column=colval, sticky="nw")
        self.attributes.append(spacer)
        
        colval += 1

        for command in commands:
            comm = tk.Label(self.command_frame, text=command.full_command(), bg=Settings.bg_color, fg=Settings.text_color, anchor="nw", 
                            font=Settings.command, justify="left", wraplength=(self._command_width * 8), width=self._command_width)
            desc = tk.Label(self.command_frame, text=command.description, bg=Settings.bg_color, fg=Settings.text_color,
                            anchor="nw", justify="left", wraplength=(self._desc_width * 8), width = self._desc_width)
            
            comm.grid(row=rowval, column=colval, sticky="nw", padx=15, pady=3)
            colval += 1
            desc.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            rowval += 1
            
            self.attributes.append(comm)
            self.attributes.append(desc)
            
            if command.options:
                options_label = tk.Label(self.command_frame, text="Options:", bg=Settings.bg_color, fg=Settings.text_color,
                                         anchor="nw", font=Settings.heading, justify="left")
                options_label.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                self.attributes.append(options_label)
                
                rowval += 1
                r = 0
                options_frame = tk.Frame(self.command_frame, bg=Settings.bg_color)
                for option in command.options:
                    options_label = tk.Label(options_frame, text="\t" + option.full_option(), bg=Settings.bg_color, fg=Settings.text_color,
                                       anchor="nw", justify="left", font=Settings.command)
                    options_label.grid(row = r, column=0, sticky="w", padx=2, pady=1)
                    if option.description:
                        options_help = tk.Label(options_frame, text=option.description, bg=Settings.bg_color, fg=Settings.text_color,
                                           anchor="nw", justify="left")
                        options_help.grid(row=r, column=1, sticky="w", padx=5, pady=1)
                        self.attributes.append(options_help)
                    self.attributes.append(options_label)
                    options_frame.grid
                    r += 1
                options_frame.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                self.attributes.append(options_frame)
                rowval += 1
            colval = 1
            
        return base_row
