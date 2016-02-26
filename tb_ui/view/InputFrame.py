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
