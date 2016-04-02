from ..view import EntryGrid
from ..model import MetaModel
import tkinter.tix as tk

class Entry():

    def __init__(self, release, app, update):
        self.release_categories = [key for key, value in release[0] if value.release]
        self.track_categories = [key for key, value in release[0] if not value.release]
        self.tracks = release
        self.release = release[0]
        self.update = update
        
        self.entry = app.input_frame
        self.meta_entry = EntryGrid.EntryGrid(self, app)

    def start(self):
        self.meta_entry.startup()

    def check_release(self, index, meta):
        """
        Check that a new release metadata input is of the correct type

        :param index: (metadata_name, track) information
        :param meta: New metadata input
        :return:    True if new meta is of the appropriate type
                    False otherwise
        """

        success = self.check_meta(meta, self.release.as_dict(), self.release_categories[index[0]])
        return success

    def check_track(self, index, meta):
        """
        Check that a new track metadata input is of the correct type

        :param index: (metadata_name, track) information
        :param meta: New metadata input
        :return:    True if new meta is of the appropriate type
                    False otherwise
        """

        # track nums will come in 1-off, so correct that
        track = self.tracks[index[1] - 1].as_dict()

        success = self.check_meta(meta, track, self.track_categories[index[0]])
        return success

    def check_meta(self, meta, audio_file, tag_name):
        """
        Check that new metadata is of the same type
        as the old metadata

        :param meta: New metadata
        :param audio_file: AudioFile as dict where metadata is changing
        :param tag_name: Name of new metadata category
        :return:    True if new meta is of the appropriate type
                    False otherwise
        """

        success = True

        old_meta = audio_file[tag_name].value
        if type(old_meta) is int:
            try:
                meta = int(meta) + 1
                print(meta)
            except ValueError:
                success = False
        return success

    def save(self):
        # update all tracks with new metadata
        for i in range(0, len(self.tracks)):
            track = self.tracks[i].as_dict()

            for k in range(0, len(self.release_categories)):
                tag = self.release_categories[k]
                meta = self.meta_entry.release.entrycget(k, 1, 'text')
                if meta == '':
                    meta = None
                track[tag].value = meta
            for k in range(0,len(self.track_categories)):
                tag = self.track_categories[k]
                track_index = i + 1
                meta = self.meta_entry.tracks.entrycget(k, track_index, 'text')
                if meta == '':
                    meta = None
                track[tag].value = meta
            self.tracks[i].save()

    def quit(self):
        self.meta_entry.destroy()
        self.update()
        self.entry.set_focus()
        
def main():
    root_dir = "Z:\C\music\Chilliwack"
    model = MetaModel.ProcessDirectory(root_dir)

    if model.has_next():
        release = model.get_next()

    r = tk.Tk()
    enter_meta = Entry(release, r)
    r.mainloop()

if __name__ == "__main__":
    main()