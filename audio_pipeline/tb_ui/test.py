import tkinter as tk
import re

tracks = re.compile('(?P<track_1>1)|(?P<track_2>2)')

curr_label = None

root = tk.Tk()

root['bg'] = 'black'

label_var = tk.StringVar()
label_var.set("hello friends!")
label_var_2 = tk.StringVar()
label_var_2.set("goodbye friends!")

entry_var = tk.StringVar()
entry_var.set("entry")


label = tk.Label(root, bg='black', activebackground='white', activeforeground='black', 
                 fg='light gray', textvariable=label_var, wraplength=200, width=50)
label_2 = tk.Label(root, bg='black', fg='light gray', activebackground='white',
                   activeforeground='black', textvariable=label_var_2, wraplength=200, width=50)

entrybox = tk.Entry(root, exportselection=0, width=50, bg='black',  
                    fg='light gray', bd=0, insertbackground='black', textvariable=entry_var)

label.pack()
label_2.pack()
entrybox.pack()

def enter_input(self, event=None):

    global curr_label

    input = entry_var.get()
    track = tracks.match(input)
    
    if track:
        if track.group('track_1'):
            print("Label 1")
            curr_label = label_var
            label['state'] = 'active'
        elif track.group('track_2'):
            print("Label 2")
            curr_label = label_var_2
            label_2['state'] = 'active'
    elif curr_label:
        print("no label?")
        curr_label.set(input)
        
entrybox.bind("<Return>", enter_input)
root.mainloop()
