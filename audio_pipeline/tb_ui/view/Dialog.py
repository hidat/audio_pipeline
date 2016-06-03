import tkinter.tix as tk
import tkinter.filedialog as filedialog


class Check(tk.Toplevel):

    def __init__(self, master, check_message, button_name, set_variable, message=None, **kwargs):
        """
        Create a dialog popup box with a checkbutton.
        :param master: Check's master
        :param check_message: Message for checkbox
        :param button: Non-cancel button
        :param message: Message
        :return:
        """
        tk.Toplevel.__init__(self, master, width=400, height=300)
        if master:
            self.master = master
        self.selected = tk.BooleanVar()
        self.set_variable = set_variable

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
        cancel_but = tk.Button(box, text="Cancel", command=self.cancel)
        select_but.bind("<Return>", select_but["command"])
        cancel_but.bind("<Return>", cancel_but["command"])

        select_but.pack(side=tk.LEFT, padx=5,pady=5)
        cancel_but.pack(side=tk.LEFT, padx=5,pady=5)
        box.pack()

    def cancel(self):
        self.set_variable.set(None)
        self.destroy()
        
    def start(self):
        self.grab_set()
        self.master.wait_window(self)
        
    def apply(self):
        # get value of checkbox
        self.set_variable.set(self.selected.get())
        
        self.destroy()

        
class MultiCheck(tk.Toplevel):

    def __init__(self, master, check_messages, button_name, on_commands, off_commands,
                    done_command, message=None, **kwargs):
        """
        Create a dialog popup box with a checkbutton.
        :param master: Check's master
        :param check_message: List of messages for each checkbox option
        :param button_name:
        :param on_commands: List of commands to perform for each checkbutton option
        :param off_commands:
        :param message: Message
        :return:
        """
        tk.Toplevel.__init__(self, master, width=400, height=300)
        if master:
            self.master = master
        self.selected = list()
        self.buttons = list()
        self.on_commands = on_commands
        self.off_commands = off_commands
        self.done_command = done_command

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

        i = 0
        for message in check_messages:
            self.selected.append(tk.BooleanVar)
            self.buttons.append(tk.Checkbutton(f, text=message, variable=self.selected[i]))
            self.buttons[i].pack()
            self.buttons[i].bind("<Return>", lambda x: self.buttons[i].toggle())
            i += 1

        box = tk.Frame(f)

        select_but = tk.Button(box, text=button_name, command=self.apply)
        cancel_but = tk.Button(box, text="Cancel", command=self.destroy)
        select_but.bind("<Return>", select_but["command"])
        cancel_but.bind("<Return>", cancel_but["command"])

        select_but.pack(side=tk.LEFT, padx=5,pady=5)
        cancel_but.pack(side=tk.LEFT, padx=5,pady=5)
        select_but.focus_set()
        box.pack()

    def start(self):
        self.grab_set()
        self.master.wait_window(self)
        
    def apply(self):
        # get value of checkbox
        for selection in self.selected:
            # when this is fully implemented, run command of all selected checkboxes
            # for now, just print
            print(str(selection))

        self.done_command()

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
        self.start()

    def start(self):
        self.grab_set();
        self.master.wait_window(self);
        
    def apply(self, command):
        command()
        self.cancel()

    def cancel(self):
        #if self.master:
        #    self.master.focus_set()
        self.destroy()


def choose_dir(directory_selector, master=None, initial_dir="\\"):
    directory_name = filedialog.askdirectory(title="fialog", parent=master, initialdir=initial_dir, mustexist=True)
    directory_selector(directory_name)


def err_message(message, ok_command, parent=None, quit=False):
    err_display = DialogBox(message, master=parent)
    buttons = [{"name": "OK", "command": ok_command}]
    if quit:
        buttons.append({"name": "Cancel", "command": err_display.cancel})
    err_display.button_box(buttons) 
