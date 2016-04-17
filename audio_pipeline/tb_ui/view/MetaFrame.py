from . import Settings
import tkinter.tix as tk

class MetaFrame(tk.Frame):

    meta_padding = {'sticky': "w", 'padx': 10, 'pady': 3}
    name_padding = {'sticky': "w", 'padx': 10, 'pady': 5}

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

    def display_meta(self, metadata):
        """
        Display metadata

        :param metadata: A list of [audiofiles] to display the metadata of
        :return:
        """
        release = metadata[0]
        rowval = 0
        colval = 0

        super().display_meta(metadata)

        for name, tag in release:
            if tag.release:
                if name not in self.labels:
                    self.attribute_text[name] = tk.StringVar()
                    self.labels[name] = tk.Label(self, release.name_style, text=name)
                    self.labels[name].grid(self.name_padding, row=rowval, column=colval)
                rowval += 1
                self.attribute_text[name].set(tag.value)
                self.attributes[name] = tk.Label(self, tag.style, textvariable=self.attribute_text[name])
                self.attributes[name].grid(self.meta_padding, row=rowval, column=colval)
                colval += 1
                rowval = 0

    def update(self, audio_file):
        for name, tag in audio_file:
            if tag.release:
                self.attribute_text[name].set(tag.value)
                self.attributes[name].config(fg=Settings.text_color)

    def select_release(self):
        self.active.clear()
        for tag, label in self.attributes.items():
            label['state'] = 'active'

class TrackFrame(MetaFrame):

    def display_meta(self, metadata):
        super().display_meta(metadata)

        padding_label = tk.Label(self, text=" ", bg=Settings.bg_color)
        padding_label.grid(row=0, column=0, padx=20, pady=3)
        rowval = 0
        colval = 1

        # Model will give us a list of audio_files already sorted by tracknum

        if not len(self.labels) > 0:
            for tag, value in metadata[0]:
                if not value.release:
                    self.labels[tag] = tk.Label(self, metadata[0].name_style, text=tag)
                    self.labels[tag].grid(self.name_padding, row=rowval, column = colval)
                    colval += 1

        colval = 1
        rowval = 1

        for track in metadata:
            name = track.file_name
            self.attributes[name] = dict()
            self.attribute_text[name] = dict()

            color = Settings.get_text_color(track)

            for tag, value in track:
                if not value.release:
                    self.attribute_text[name][tag] = tk.StringVar()
                    self.attribute_text[name][tag].set(value.value)
                    self.attributes[name][tag] = tk.Label(self, value.style, foreground=color,
                                                          textvariable=self.attribute_text[name][tag])
                    self.attributes[name][tag].grid(self.meta_padding, row=rowval, column=colval)
                    colval += 1
            rowval += 1
            colval = 1

    def clear(self):
        for file, tags in self.attributes.items():
            for name, label in tags.items():
                label.destroy()

    def update(self, audio_file):
        name = audio_file.file_name
        color = Settings.get_text_color(audio_file)
        for tag, value in audio_file:
            if not value.release:
                if value.value:
                    self.attribute_text[name][tag].set(value.value)
                else:
                    self.attribute_text[name][tag].set("")
                self.attributes[name][tag].config(fg=color)

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