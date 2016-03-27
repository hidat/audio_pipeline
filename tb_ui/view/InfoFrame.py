from . import Settings
import tkinter as tk


class InfoFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        self.master = master
        self.grid()

    def display_commands(self):
        """
        Display information about available commands onscreen

        :return:
        """
        rowval = 0
        colval = 0

        desc = tk.Label(self, text="Commands", bg=Settings.bg_color, fg=Settings.text_color,
                        anchor="nw", font=Settings.heading)
        desc.grid(row=rowval, column=colval, padx=5, pady=3)

        rowval = 1
        colval = 1

        for command in Settings.commands:
            comm = tk.Label(self, text=command.command, bg=Settings.bg_color, fg=Settings.text_color,
                            anchor="nw", font=Settings.heading, justify="left")
            desc = tk.Label(self, text=command.help, bg=Settings.bg_color, fg=Settings.text_color,
                            anchor="nw", justify="left")

            comm.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            colval += 1
            desc.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            rowval += 1

            for ex in command.examples:
                example_title = tk.Label(self, text="Example:", bg=Settings.bg_color, fg=Settings.text_color,
                                         anchor="nw", font=Settings.heading, justify="left")
                example = tk.Label(self, text="\t" + ex, bg=Settings.bg_color, fg=Settings.text_color,
                                   anchor="nw", justify="left")
                example_title.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                rowval += 1
                example.grid(row=rowval, column=colval, sticky="w", padx=2, pady=2)
                rowval += 1
            colval = 1
