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
        self.input_processor = input_processor

        tk.Frame.__init__(self, master, bg=Settings.bg_color)

    def allow_input(self):
        """
        Use an entry box to retrieve user input
        """
        self.entrybox = tk.Entry(self, exportselection=0)
        self.entrybox.grid()

        self.input_value = tk.StringVar()
        self.input_value.set("Enter input")
        self.entrybox['textvariable'] = self.input_value
        self.entrybox.focus_set()
        self.entrybox.select_range(0, tk.END)

        self.entrybox.bind('<Key-Return>', self.input_processor)

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