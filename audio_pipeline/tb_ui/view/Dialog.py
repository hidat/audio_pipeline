import tkinter.tix as tk
import tkinter.filedialog as filedialog


class Check(tk.Toplevel):

    def __init__(self, master, check_message, button_name, on_command, off_command, message=None, **kwargs):
        """
        Create a dialog popup box with a checkbutton.
        :param master: Check's master
        :param check_message: Message for checkbox
        :param button: Non-cancel button
        :param message: Message
        :return:
        """
        tk.Toplevel.__init__(self, master, width=400, height=300)
        self.master = master
        self.selected = tk.BooleanVar()
        self.on_command = on_command
        self.off_command = off_command

        if self.master:
            self.transient(master)
            location = "+" + str(int(self.master.winfo_rootx() + self.master.winfo_width() / 2)) +\
                       "+" + str(int(self.master.winfo_rooty() + self.master.winfo_height() / 2))
            self.geometry(location)

        f = tk.Frame(self, width=500, height=500)
        f.pack()
        if message:
            l = tk.Label(f, text=message)
            l.pack()

        c = tk.Checkbutton(f, text=check_message, variable=self.selected)
        c.pack()
        c.select()
        c.focus_set()
        c.bind("<Return>", lambda x: c.toggle())

        box = tk.Frame(f)

        select_but = tk.Button(box, text=button_name, command=self.apply)
        cancel_but = tk.Button(box, text="Cancel", command=self.destroy)
        select_but.bind("<Return>", select_but["command"])
        cancel_but.bind("<Return>", cancel_but["command"])

        select_but.pack(side=tk.LEFT, padx=5,pady=5)
        cancel_but.pack(side=tk.LEFT, padx=5,pady=5)
        box.pack()

    def start(self):
        self.grab_set()
        self.master.wait_window(self)
        
    def apply(self):
        # get value of checkbox
        on = self.selected.get()

        if on:
            self.on_command()
        else:
            print(self.off_command)
            self.off_command()

        self.destroy()


class DialogBox(tk.Toplevel):

    def __init__(self, message, buttons=None, dimensions=(100,75), title=None, master=None):
        """
        Create a dialog popup box containing the specified message string and button options.
        
        :param message: string message to display in popup
        :param buttons: List of button dictionaries; each button dictionary must contain
                        {"name": name, "command": command}
        """
        tk.Toplevel.__init__(self, master, width=dimensions[0], height=dimensions[1])
        if master:
            self.master = master
            self.transient(master)
            location = "+" + str(int(self.master.winfo_rootx() + self.master.winfo_width() / 2)) +\
                       "+" + str(int(self.master.winfo_rooty() + self.master.winfo_height() / 2))
            self.geometry(location)

        if title:
            self.title(title)

        self.text(message)
        if buttons:
            self.button_box(buttons)

    def text(self, message):
        label = tk.Label(self, text=message)
        label.pack()
        
    def button_box(self, buttons):
        box = tk.Frame(self)
        
        for i in range(0, len(buttons)):
            button = buttons[i]
            if "command" in button and button["command"]:
                but = tk.Button(box, text=button["name"], command=lambda x=button["command"]: self.apply(x))
            else:
                but = tk.Button(box, text=button["name"], command=self.cancel)
            if i == 0:
                but.focus_set()
                
            but.bind("<Return>", but['command'])
            but.pack(side=tk.LEFT, padx=5,pady=5)

        box.pack()

    def start(self):
        self.grab_set();
        self.master.wait_window(self);
        
    def apply(self, command):
        command()
        self.cancel()

    def cancel(self):
        if self.master:
            self.master.focus_set()
        self.destroy()


def choose_dir(directory_selector, master=None, initial_dir="\\"):
    directory_name = filedialog.askdirectory(title="fialog", parent=master, initialdir=initial_dir, mustexist=True)
    directory_selector(directory_name)