import tkinter as tk
import tkinter.filedialog as filedialog
from Util import *


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
        choose_dir(self.directory_selector, master=self)
        
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
        quit_message("Close Meta Reviewer?", self.quit, self)
        
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
