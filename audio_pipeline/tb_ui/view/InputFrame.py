import tkinter.tix as tk
from . import Settings


class InputFrame(tk.Frame):
    def __init__(self, input_processor, label=None, master=None):
        if label:
            self.label = tk.Label(self, bg=Settings.bg_color, fg=Settings.text_color, text=label)
            self.label.grid(row=0, column=0)
        else:
            self.label = None
        self.entrybox = None
        self.input_value = None
        self.prev_button = None
        self.next_button = None
        self.input_processor = input_processor

        tk.Frame.__init__(self, master, bg=Settings.bg_color)

    def allow_input(self):
        """
        Use an entry box to retrieve user input
        """
        label = tk.Label(self, bg=Settings.bg_color, fg=Settings.text_color, text="Input>> ", font=Settings.heading)
        label.grid(row=0, column=0, padx=20, pady=15)
        self.entrybox = tk.Entry(self, exportselection=0, width=50, bg=Settings.bg_color, 
                                 fg=Settings.text_color, bd=0, font=Settings.standard, insertbackground=Settings.text_color)
        self.entrybox.grid(row=0, column=1, padx=10)

        self.input_value = tk.StringVar()
        self.input_value.set("Enter input")
        self.entrybox['textvariable'] = self.input_value
        
        self.set_focus()
        self.entrybox.bind('<Key-Return>', self.process_input)

    def nav_buttons(self):
        self.prev_button = tk.Button(self, takefocus=False, text="Prev", width=8, underline=0, command=self.nav_prev)
        self.next_button = tk.Button(self, takefocus=False, text="Next", width=8, underline=0, command=self.nav_next)
        
        if self.entrybox:
            self.prev_button.grid(row=0, column=2, padx=10)
            self.next_button.grid(row=0, column=3, padx=10)
            
    def nav_prev(self):
        self.input_processor("prev")
    
    def nav_next(self):
        self.input_processor("next")

    def set_focus(self):
        self.bind_class("Entry", "<Key-Return>", lambda x: None)
        self.entrybox.focus_set()
        self.entrybox.select_range(0, tk.END)

    def process_input(self, event):
        input_string = self.get_input()
        self.input_processor(input_string)
        
    def get_input(self):
        if self.entrybox:
            contents = self.input_value.get()
        return contents

    def select_input(self):
        if self.entrybox:
            self.entrybox.select_range(0, tk.END)

    def clear_input(self):
        if self.entrybox:
            self.entrybox.delete(0, tk.END)

    def close_frame(self):
        self.destroy()
