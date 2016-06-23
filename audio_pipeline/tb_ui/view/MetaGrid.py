import tkinter.tix as tk
from . import Dialog


class MetaGrid(tk.Grid):

    def __init__(self, update_command, last_command, bindings, start_index,
                 forbidden_rows, forbidden_columns, *args, **kwargs):
        kwargs['editnotify'] = self.editnotify
        tk.Grid.__init__(self, *args, **kwargs)
        self.update_command = update_command
        self.last_command = last_command
        if 'width' in kwargs and 'height' in kwargs:
            self.start = start_index
            self.final = (int(self['width']) - 1, int(self['height']) - 1)
            
        self.bindings = bindings
        self.forbidden_rows = forbidden_rows
        self.forbidden_columns = forbidden_columns
        self.curr_pos = self.start
        self.curr_meta = " "

    def editapply(self):
        self.edit_apply()
        if self.curr_pos:
            return self.move()
        
    def editnotify(self, x, y):
        # make a map of position -> (track, metadata) for use here
        # There has got to be a better way to bind tab and return to the selected cell entry
        # But I haven't found it yet! So this is what we'll do for now.
        x = int(x)
        y = int(y)
        self.curr_pos = (x, y)
        self.curr_meta = self.entrycget(x, y, 'text')
        if not self.bindings():
            # These are all class-level bindings, that are unbound when this app is closed
            # However, some of these class-level bindings override previous default bindings
            # which are not restored when these are unbound on closure, and may effect
            # entry behavior in general TB
            self.bind_class("Entry", "<Tab>", lambda x: self.move_cell(self.right, x))
            self.bind_class("Entry", "<Return>", lambda x: self.move_cell(self.down))
            self.bind_class("Entry", "<Up>", lambda x: self.move_cell(self.up))
            self.bind_class("Entry", "<Down>", lambda x: self.move_cell(self.down))
            self.bind_class("Entry", "<Shift-Tab>", lambda x: self.move_cell(self.left))
            self.bind_class("Entry", "<Shift-Left>", lambda x: self.move_cell(self.left))
            self.bind_class("Entry", "<Shift-Right>", lambda x: self.move_cell(self.right))
            self.bind_class("Entry", "<Shift-Up>", lambda x: self.move_cell(self.up))
            self.bind_class("Entry", "<Shift-Down>", lambda x: self.move_cell(self.down))
            self.bind_class("Entry", "<Control-z>", self.restore_meta)
        return True

    def restore_meta(self, event):
        print("restoring: " + self.curr_meta)
        meta = self.curr_meta
        position = self.curr_pos
        self.edit_set(self.start[0], self.start[1])
        self.set(position[0], position[1], text=meta)
        self.edit_set(position[0], position[1])
        
    def move(self):
        success = False
        pos = self.curr_pos
        meta = self.entrycget(pos[0], pos[1], 'text')
        new_meta = self.update_command(pos, meta)
        if new_meta:
            self.set(pos[0], pos[1], text=new_meta)
            success = True
        else:
            # display an error message
            self.set(pos[0], pos[1], text=meta)
            self.set_curr_cell()
            Dialog.err_message("Please enter appropriate metadata", ok_command=self.set(pos[0], pos[1], text=meta))
        return success
    
    def move_cell(self, direction_command, event=None):
        success = self.editapply()
        
        if success:
            pos = direction_command(self.curr_pos)
            while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                pos = direction_command(pos)
            if pos:
                self.set_cell(pos)
        return "break"

    # def move_cell(self, direction_command, event=None):
        # # apply edit so new metadata can be retrieved
        # self.edit_apply()

        # pos = self.curr_pos
        # meta = self.entrycget(pos[0], pos[1], 'text')
        # new_meta = self.update_command(pos, meta)

        # if new_meta:
            # # If entered metadata is valid, formatting may occur in update_command, so set the cell
            # self.set(pos[0], pos[1], text=new_meta)
            # pos = direction_command(self.curr_pos)
            # while pos and (pos[0] in self.forbidden_columns or pos[1] in self.forbidden_rows):
                    # pos = direction_command(pos)
        # else:
            # # Entered metadata is invalid, so display an error message
            # Dialog.err_message("Please enter appropriate metadata", ok_command=self.set(pos[0], pos[1], text=meta))
            # self.set_curr_cell()
        # if pos:
            # self.set_cell(pos)
        # return "break"

        
    def up(self, curr):
        if curr == self.start:
            # going up we will not loop????
            pos = curr
        elif curr[1] == 1:
            # At top of column - loop to end of previous column
            pos = curr[0] - 1, int(self['height']) - 1
        else:
            # not at the end of the grid or the end of the column - just move up one row
            pos = curr[0], curr[1] - 1
            
        return pos
        
    def down(self, curr):
        # check if we need to update metadata
        if curr == self.final:
            # call a passed method
            pos = self.last_command()
        elif curr[1] == int(self['height']) - 1:
            # loop to the start of the next column
            pos = (curr[0] + 1, self.start[1])
        else:
            # not at the end of the grid or the end of the column - just move down one row
            pos = (curr[0], curr[1] + 1)
            
        return pos
            
    def right(self, curr):
        if curr == self.final:
            # call the passed 'final' method
            # behavior in the final cell is the same for return and tab
            pos = self.last_command()
        elif curr[0] == int(self['width']) - 1:
            # loop to the start of the next row
            pos = (self.start[0], curr[1] + 1)
        else:
            # not at the end of the grid or the end of the row
            # just move over one column (in the same row)
            pos = (curr[0] + 1, curr[1])
            
        return pos
        
    def left(self, curr):
        if curr == self.start:
            # right now we're just gonna not move
            pos = curr
        elif curr[0] == self.start[0]:
            # loop to the end of the previous row
            pos = (int(self['width']) - 1, curr[1] - 1)
        else:
            # not at the end of the grid or the end of the row
            # move one column to the left (in the same row)
            pos = (curr[0] - 1, curr[1])
            
        return pos
            
    def set_curr_cell(self):
        self.set_cell(self.curr_pos)
        
    def set_cell(self, pos):
        self.anchor_set(pos[0], pos[1])
        self.edit_set(pos[0], pos[1])
        