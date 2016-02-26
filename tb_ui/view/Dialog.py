class DialogBox(tk.Toplevel):

    def __init__(self, message, buttons=None, dimensions=(100,75), cancel=False, title=None, master=None):
        """
        Create a dialog popup box containing the specified message string and button options.
        
        :param message: string message to display in popup
        :param buttons: List of button directories; each button directory must contain
                        {"name": name, "command": command}
        """
        tk.Toplevel.__init__(self, master, width=dimensions[0], height=dimensions[1])
        if master:
            self.master = master
            self.transient(master)
            location = "+" + str(self.master.winfo_rootx() + 50) +\
                       "+" + str(self.master.winfo_rooty() + 50)
            self.geometry(location)
            
        if title:
            self.title(title)
            
        self.text(message)
        if buttons:
            self.button_box(buttons)
            
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
    def text(self, message):
        label = tk.Label(self, text=message)
        label.pack()
        
    def button_box(self, buttons):
        box = tk.Frame(self)
        
        for i in range(0, len(buttons)):
            button = buttons[i]
            if not "command" in button.keys() or not button["command"]:
                button["command"] = self.cancel
            but = tk.Button(box, text=button["name"], command=lambda x=button["command"]: self.apply(x))
            if i == 0:
                but.focus_set()
                
            but.bind("<Return>", but['command'])
            but.pack(side=tk.LEFT, padx=5,pady=5)

        box.pack()
        self.wait_window(self)
    
    def apply(self, command):
        self.cancel()
        command()

    def cancel(self):
        self.destroy()
        
def choose_dir(directory_selector, master=None, initial_dir="\\"):
    directory_name = filedialog.askdirectory(title="fialog", parent=master, initialdir=initial_dir, mustexist=True)
    directory_selector(directory_name)
    
def quit_message(message, quit_command, parent=None):
    quit_display = DialogBox(message, master=parent)
    buttons = [{"name": "Close", "command": quit_command}, {"name": "Cancel", "command": quit_display.cancel}]
    quit_display.button_box(buttons)
    
def err_message(message, ok_command, parent=None, quit=False):
    err_display = DialogBox(message, master=parent)
    buttons = [{"name": "OK", "command": ok_command}]
    if quit:
        buttons.append({"name": "Quit", "command": err_display.cancel})
    err_display.button_box(buttons)