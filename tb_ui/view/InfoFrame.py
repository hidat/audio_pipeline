import view.Settings as Settings

class InfoFrame(tk.Frame):
    # the information frame should open in a new window, because some people might want to reference it?
    
    def __init__(self, close_command, master=None):
        tk.Frame.__init__(self, master, bg=bg_color)
        self.master.protocol("WM_DELETE_WINDOW", close_command)
        self.grid()
        
    def display_commands(self):
        """
        Displays a passed dictionary of command -> command effects onscreen
        """
        row_index = 0
        col_index = 0
        
        description_label = tk.Label(self, text="Commands", bg=bg_color, fg=text_color, anchor="nw", font=heading)
        description_label.grid(row=row_index, column=col_index, padx=5, pady=3)
        
        row_index += 1
        col_index += 1
                        
        for command in Settings.commands:
            comm = tk.Label(self, text=command.command, bg=Settings.bg_color, fg=Settings.text_color, anchor="nw", font=heading, justify="left")
            desc = tk.Label(self, text=command.help, bg=Settings.bg_color, fg=Settings.text, anchor="nw", justify="left")
            comm.grid(row=row_index, column=col_index, sticky="nw", padx=5, pady=3)
            col_index += 1
            desc.grid(row=row_index, column=col_index, sticky="nw", padx=5, pady=3)
            row_index += 1
            for ex in command.examples:
                example_title = tk.Label(self, text="Example:", bg=Settings.bg_color, fg=Settings.text, anchor="nw", font=heading, justify="left")
                example_title.grid(row=row_index, column=col_index, sticky="w", padx=2, pady=1)
                row_index += 1
                ex = tk.Label(self, text="\t" + ex, bg=Settings.bg_color, fg=Settings.text, anchor="nw", justify="left")
                example.grid(row=row_index, column=col_index, sticky="w", padx=2, pady=2)
                row_index += 1
            col_index = 1
        
        self.focus_set()
            
    def cancel(self):
        if master:
            self.master.focus_set()
        self.destroy()
        return None    
