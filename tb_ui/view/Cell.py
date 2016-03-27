import tkinter as tk

class Cell(tk.Frame):
    x = 0
    y = 0

    def __init__(self, width, text="", master=None):
        tk.Frame.__init__(self)
        self.master = master
        self.width = width
        self.value = tk.StringVar()
        self.value.set(text)
        self.entry = tk.Entry(self, exportselection=0, textvariable=self.value, width=self.width)
        self.label = tk.Label(self, textvariable=self.value, width=self.width)
        self.label.grid(row=self.x, column=self.y)
        self.grid()

    def select(self):
        self.entry.grid(row=self.x, column=self.y)

    def unselect(self):
        # there is definitely a way to like. un-grid something. without destroying it. haha
        self.entry.destroy()
        self.entry = tk.Entry(self, exportselection=0, textvariable=self.value, width=self.width)