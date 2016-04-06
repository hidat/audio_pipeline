from . import Settings
import tkinter.tix as tk

class ReleaseFrame(tk.Frame):
    def __init__(self, master=None):
        """
        A frame to display metadata information

        :param master: Frame's master
        :return:
        """
        self.master = master

        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        self.attributes = {}
        self.labels = {}

    def display_meta(self, metadata):
        """
        Display metadata

        :param metadata: A list of [audiofiles] to display the metadata of
        :return:
        """
        self.clear()
        self.attributes.clear()
        release = metadata[0]

        rowval = 0
        colval = 0

        for name, tag in release:
            if tag.release:
                if name not in self.labels:
                    self.labels[name] = tk.Label(self, text=name, anchor="nw", fg=Settings.text_color, bg=Settings.bg_color, font=Settings.heading)
                    self.labels[name].grid(row=rowval, column=colval, sticky="w", padx=10, pady=5)
                rowval += 1
                self.attributes[name] = tk.Label(self, text=tag.value, anchor="nw", fg=Settings.text_color, bg=Settings.bg_color, font=Settings.standard)
                self.attributes[name].grid(row=rowval, column=colval, sticky="w", padx=10, pady=3)
                colval += 1
                rowval = 0

    def update(self, audio_file):
        for name, tag in audio_file:
            if tag.release:
                self.attributes[name].config(text=tag.value, fg=Settings.text_color)

    def clear(self):
        for name, label in self.attributes.items():
            label.destroy()

    def close(self):
        self.destroy()

class TrackFrame(tk.Frame):
    
    def __init__(self, master=None):
        """
        A frame to display track metadata

        :param master: God king of this frame
        :return:
        """
        self.master = master
        tk.Frame.__init__(self, master, bg=Settings.bg_color)
        self.attributes = {}
        self.labels = {}

    def display_meta(self, metadata):
        self.clear()
        self.attributes.clear()
        bg_color = Settings.bg_color

        padding_label = tk.Label(self, text="        ", bg=bg_color)
        padding_label.grid(row=0, column=0)
        rowval = 0
        colval = 1

        # Model will give us a list of audio_files already sorted by tracknum

        if not len(self.labels) > 0:
            for tag, value in metadata[0]:
                if not value.release:
                    self.labels[tag] = tk.Label(self, text=tag, anchor="nw", fg=Settings.text_color, bg=Settings.bg_color, font=Settings.heading)
                    self.labels[tag].grid(row=rowval, column = colval, sticky="w", padx=10, pady=5)
                    colval += 1

        colval = 1
        rowval = 1

        for track in metadata:
            name = track.file_name
            self.attributes[name] = {}

            color = Settings.get_text_color(track)

            for tag, value in track:
                if not value.release:
                    self.attributes[name][tag] = tk.Label(self, text=value.value, anchor="nw", fg=color, bg=bg_color, font=Settings.standard)
                    self.attributes[name][tag].grid(row=rowval, column=colval, sticky="w", padx=10, pady=3)
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
                    self.attributes[name][tag].config(text=value.value, fg=color)
                else:
                    self.attributes[name][tag].config(text="", fg=color)

    def close(self):
        self.destroy()