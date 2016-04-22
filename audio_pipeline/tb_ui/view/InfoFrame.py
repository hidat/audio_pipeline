from . import Settings
import tkinter.tix as tk


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
                            anchor="nw", font=Settings.command, justify="left")
            desc = tk.Label(self, text=command.help, bg=Settings.bg_color, fg=Settings.text_color,
                            anchor="nw", justify="left")

            comm.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            colval += 1
            desc.grid(row=rowval, column=colval, sticky="nw", padx=5, pady=3)
            rowval += 1

            if command.sub_commands:
                sub_title = tk.Label(self, text=command.sub_commands.name, bg=Settings.bg_color, fg=Settings.text_color,
                                         anchor="nw", font=Settings.heading, justify="left")
                sub_title.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                rowval += 1
                r = 0
                sub_frame = tk.Frame(self, bg=Settings.bg_color)
                for c in command.sub_commands.commands:
                    sub_command = tk.Label(sub_frame, text="\t" + c.command, bg=Settings.bg_color, fg=Settings.text_color,
                                       anchor="nw", justify="left", font=Settings.command)
                    sub_help = tk.Label(sub_frame, text=c.help, bg=Settings.bg_color, fg=Settings.text_color,
                                       anchor="nw", justify="left")
                    sub_command.grid(row = r, column=0, sticky="w", padx=2, pady=2)
                    sub_help.grid(row=r, column=1, sticky="w", padx=5, pady=2)
                    sub_frame.grid
                    r += 1
                sub_frame.grid(row=rowval, column=colval, sticky="w", padx=2, pady=2)
                rowval += 1


                                   
            if command.examples > []:
                example_title = tk.Label(self, text="Example:", bg=Settings.bg_color, fg=Settings.text_color,
                                         anchor="nw", font=Settings.heading, justify="left")
                example_title.grid(row=rowval, column=colval, sticky="w", padx=2, pady=1)
                rowval += 1
                for ex in command.examples:
                    example = tk.Label(self, text="\t" + ex, bg=Settings.bg_color, fg=Settings.text_color,
                                       anchor="nw", justify="left")
                    example.grid(row=rowval, column=colval, sticky="w", padx=2, pady=2)
                    rowval += 1
            colval = 1
