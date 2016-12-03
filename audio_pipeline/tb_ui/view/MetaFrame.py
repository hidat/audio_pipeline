from . import Settings
import tkinter.tix as tk
from .. import get_text_color, track_tags, release_tags


__max_width__ = 260


class MetaFrame(tk.Frame):

    meta_padding = {'sticky': "w", 'padx': 10, 'pady': 3}
    name_padding = {'sticky': "w", 'padx': 10, 'pady': 5}
    tag_style = {'anchor': 'nw', 'bg': Settings.bg_color, 'foreground': Settings.text_color, 
                                 'font': Settings.standard, 'activeforeground': Settings.active_fg,
                                 'activebackground': Settings.active_bg, 'justify': 'left'}
    name_style = {'anchor': 'nw', 'justify': 'left', 'background': Settings.bg_color,
                  'foreground': Settings.text_color, 'font': Settings.heading}

    def __init__(self, master=None):
        """
        A frame to display metadata information

        :param master: God king of this frame
        :return:
        """
        self.master = master

        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        self.attributes = {}
        self.labels = {}
        self.attribute_text = {}
        self.attribute_widths = []

        self.active = []

    def display_meta(self, metadata):
        self.clear()
        self.attributes.clear()

    def clear(self):
        for name, label in self.attributes.items():
            label.destroy()

    def close(self):
        self.destroy()


class ReleaseFrame(MetaFrame):

    default_cell_width = 15

    def __init__(self):
        super().__init__()
        self.labels = []

    def add_tag(self, tag_info, colval):
        self.attribute_text[tag_info.tag.name] = tk.StringVar()
        self.labels[tag_info.row][tag_info.tag.name] = tk.Label(self, self.name_style, text=tag_info.tag.name)
        self.labels[tag_info.row][tag_info.tag.name].grid(self.name_padding, row=(tag_info.row * 2), column=colval)
        colval += 1
        self.attribute_widths.append(tag_info.width)
        return colval

    def display_meta(self, metadata):
        """
        Display metadata

        :param metadata: A list of [audiofiles] to display the metadata of
        :return:
        """
        track = metadata[0]
        rowval = 0
        colval = 0

        super().display_meta(metadata)
        
        try:
            total_width = 0
            rowidth = 0
            fields_per_row = -1
            self.labels.append({})
            for tag_info in track.tb_release():
                total_width += (tag_info.width + self.name_padding['padx'])
                rowidth += (tag_info.width + self.name_padding['padx'])
                if total_width < __max_width__:
                    fields_per_row += 1
                elif colval > fields_per_row or rowidth > __max_width__:
                    rowval += 1
                    colval = 1
                    rowidth = (tag_info.width + self.name_padding['padx'])
                    if rowval == len(self.labels):
                        self.labels.append({})

                if tag_info.tag.name not in self.labels[rowval]:
                    display_name = tag_info.tag.name
                    for r in release_tags:
                        if r.command == display_name:
                            if r.display_name:
                                display_name = r.display_name
                            break
                    self.attribute_text[tag_info.tag.name] = tk.StringVar()
                    self.labels[rowval][tag_info.tag.name] = tk.Label(self, self.name_style,
                                                                            text=display_name)
                    self.labels[rowval][tag_info.tag.name].grid(self.name_padding, row=(rowval * 2),
                                                                      column=colval)
                    self.attribute_widths.append(tag_info.width)
                    # colval = self.add_tag(tag_info, colval)
                    colval += 1
        except AttributeError:
            pass
            
        width_index = 0
        for tag in track.release():
            name = tag.name
            for label_group in self.labels:
                if name in label_group and width_index < len(self.attribute_widths):

                    column_value = label_group[name].grid_info()["column"]
                    row_value = label_group[name].grid_info()["row"] + 1
                    self.attribute_text[name].set(str(tag))
                    self.attributes[name] = tk.Label(self, self.tag_style, width=self.attribute_widths[width_index],
                                                     wraplength=(self.attribute_widths[width_index] * 8),
                                                     textvariable=self.attribute_text[name])
                    self.attributes[name].grid(self.meta_padding, row=row_value, column=column_value)
                    width_index += 1

    def update_meta(self, audio_file):
        for tag in audio_file.release():
            for label_group in self.labels:
                if tag.name in label_group:
                    self.attribute_text[tag.name].set(str(tag))
                    self.attributes[tag.name].config(fg=Settings.text_color)

    def select_release(self):
        self.active.clear()
        for tag, label in self.attributes.items():
            label['state'] = 'active'


class TrackFrame(MetaFrame):

    default_cell_width = 25

    def add_tag(self, tag, width, rowval, colval):
        display_name = tag.name
        for t in track_tags:
            if t.command == display_name:
                if t.display_name:
                    display_name = t.display_name
                break

        self.labels[tag.name] = tk.Label(self, self.name_style, text=display_name)
        self.labels[tag.name].grid(self.name_padding, row=rowval, column=colval)
        colval += 1
        self.attribute_widths.append(width)
        return rowval, colval

    def display_meta(self, metadata):
        super().display_meta(metadata)

        padding_label = tk.Label(self, text=" ", bg=Settings.bg_color)
        padding_label.grid(row=0, column=0, padx=20, pady=3)
        rowval = 0
        colval = 1

        # Model will give us a list of audio_files already sorted by tracknum

        if not len(self.labels) > 0:
            
            track = metadata[0]
            
            try:
                for t in track.tb_track():
                    rowval, colval = self.add_tag(t.tag, t.width, rowval, colval)
            except AttributeError:
                # this should only happen on the obscenity rating - pass
                pass
                
        colval = 1
        rowval = 1

        for track in metadata:
            name = track.file_name
            self.attributes[name] = dict()
            self.attribute_text[name] = dict()
                    
            color = get_text_color(track)
            width_index = 0
            for tag in track.track():
                if tag.name in self.labels and width_index < len(self.attribute_widths):
                    self.attribute_text[name][tag.name] = tk.StringVar()
                    self.attribute_text[name][tag.name].set(tag)
                    self.attributes[name][tag.name] = tk.Label(self, self.tag_style, foreground=color,
                                                          width=self.attribute_widths[width_index], 
                                                          wraplength=(self.attribute_widths[width_index]*8),
                                                          textvariable=self.attribute_text[name][tag.name])
                    self.attributes[name][tag.name].grid(self.meta_padding, row=rowval, column=colval)
                    width_index += 1
                    colval += 1
            rowval += 1
            colval = 1

    def clear(self):
        for file, tags in self.attributes.items():
            for name, label in tags.items():
                label.destroy()

    def update_meta(self, audio_file):
        name = audio_file.file_name
        color = get_text_color(audio_file)
        i = 0
        for tag in audio_file.track():
            if tag.name in self.labels and i < len(self.attribute_widths):
                self.attribute_text[name][tag.name].set(tag)
                self.attributes[name][tag.name].config(fg=color)
                i += 1

    def select_tracks(self, tracks):
        self.active.clear()
        for track_name, track in self.attributes.items():
            if track_name in tracks:
                for tag, label in track.items():
                    label['state'] = 'active'
            else:
                for tag, label in track.items():
                    label['state'] = 'normal'

    def select_tags(self, tag):
        for track_name, track in self.attributes.items():
            for name, label in track.items():
                if label['state'] == 'active' and name == tag:
                    self.active.append(self.attribute_text[name])
                else:
                    label['state'] = 'normal'
