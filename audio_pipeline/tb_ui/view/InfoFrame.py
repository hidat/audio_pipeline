from . import Settings
from .. import release_tags, track_tags, general_commands, tag_command_help
import tkinter.tix as tk
        
selected_bg = "gray"
        
class InfoFrame(tk.Frame):
    _command_width = 30
    _desc_width = 70
    
    def __init__(self, master=None, base_name=None):
        self.base_name = base_name
        self.desc = None
        self.command_frame = None
        self.master = master
        self.gen_help = None
                
        width_frame = tk.Frame(master=self.master, bg=Settings.bg_color, width=115*8, height=0)
        width_frame.grid(row=0, column=1, padx=5, pady=3, sticky="nw")
        height_frame = tk.Frame(master=self.master, bg=Settings.bg_color, height=70*8, width=0)
        height_frame.grid(row=1, column=0, padx=5, pady=3, sticky="nw")

        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        self.menubar = tk.Menu(self.master, takefocus=True)
        self.menubar.add_command(label="General Commands", command=lambda: self.display_commands(general_commands, "General Commands", 1))
        self.menubar.add_command(label="Track Commands", command=lambda: self.display_commands(track_tags, "Track Metadata", 3, tag_command_help))
        self.menubar.add_command(label="Release Commands", command=lambda: self.display_commands(release_tags, "Release Metadata", 5, tag_command_help))
        self.master.config(menu=self.menubar)
        self.menubar.activate(1)
        self.menubar.invoke(1)
        self.menubar.focus_set()
        self.grid(row=1, column=1, padx=5, pady=3, sticky="nw")


    def display_commands(self, commands, section_header, index, gen_help=None):
        """
        Display information about available commands onscreen

        :return:
        """ 
        wname = self.base_name + section_header
        self.master.title(wname)
        desc = tk.Label(self, text=section_header, bg=Settings.bg_color, fg=Settings.text_color,
            anchor="nw", font=Settings.heading)
        desc.grid(row=0, column=0, padx=5, pady=3, sticky="nw")
        if self.gen_help:
            self.gen_help.destroy()
            self.gen_help = None
        if gen_help:
            desc_help = tk.Label(self, text=gen_help, bg=Settings.bg_color, fg=Settings.text_color,
                                 anchor="nw")
            desc_help.grid(row=1, column=0, padx=5, pady=3, sticky="nw")
            self.gen_help = desc_help
        if self.desc:
            self.desc.destroy()
            self.desc = None
        self.desc = desc
        
        if self.command_frame:
            self.command_frame.destroy()
            self.command_frame = None
        self.populate_frame(commands, 1, section_header)
            
    def populate_frame(self, commands, base_row, section_header):        
        base_row += 1
        
        self.command_frame = tk.Frame(self, bg=Settings.bg_color)
        self.command_frame.grid(row=base_row, column=0, sticky="nw")
        
        base_row += 1
        
        rowval = 0
        colval = 0

        spacer = tk.Label(self.command_frame, text="\t\t", bg=Settings.bg_color)
        spacer.grid(row=rowval, column=colval, sticky="nw")
        
        colval += 1

        for command in commands:
            comm = tk.Label(self.command_frame, text=command.full_command(), bg=Settings.bg_color, fg=Settings.text_color, anchor="nw", 
                            font=Settings.command, justify="left", wraplength=(self._command_width * 8), width=self._command_width)
            desc = tk.Label(self.command_frame, text=command.description, bg=Settings.bg_color, fg=Settings.text_color,
                            anchor="nw", justify="left", wraplength=(self._desc_width * 7), width = self._desc_width + 10)
            
            comm.grid(row=rowval, column=colval, sticky="nw", padx=15, pady=3)
            colval += 1
            desc.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            rowval += 1
                        
            if command.options:
                options_label = tk.Label(self.command_frame, text="Options:", bg=Settings.bg_color, fg=Settings.text_color,
                                         anchor="nw", font=Settings.heading, justify="left")
                options_label.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                
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
                    options_frame.grid
                    r += 1
                options_frame.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                rowval += 1
            colval = 1
            
        return base_row
