from ..util import InputPatterns
from ..view import EntryGrid
from ...util import Util
from audio_pipeline.util import Exceptions


class Entry():

    def __init__(self, release, app, update):
        self.tracks = release
        self.release = release[0].release()
        self.track = release[0].track()
        self.track = [self.tracks[0].track_num, self.tracks[0].title, self.tracks[0].artist, self.tracks[0].length]
        try:
            self.track.append(self.tracks[0].obscenity)
            self.track.append(self.tracks[0].radio_edit)
        except AttributeError:
            pass
            
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

        release_dict = {tag.name: tag for tag in self.release}
        
        new_meta = self.check_meta(meta, release_dict, self.meta_entry.release_categories[index[0]])
        return new_meta

    def check_track(self, index, meta):
        """
        Check that a new track metadata input is of the correct type

        :param index: (metadata_name, track) information
        :param meta: New metadata input
        :return:    True if new meta is of the appropriate type
                    False otherwise
        """

        # track nums will come in 1-off, so correct that
        track = self.tracks[index[1] - 1].track()
        track_dict = {tag.name: tag for tag in track}
        
        new_meta = self.check_meta(meta, track_dict, self.meta_entry.track_categories[index[0]])
        return new_meta

    def check_meta(self, meta, audio_file, tag_name):
        """
        Check that metadata is of the same type as the old metadata,
        and perform any transformation to get appropriate metadata.

        :param meta: New metadata
        :param audio_file: AudioFile as dict where metadata is changing
        :param tag_name: Name of new metadata category
        :return:    New metadata if possible
                    None if new metadata is of incorrect type
        """

        old_meta = audio_file[tag_name].value
        new_meta = None
        if meta:
            if type(old_meta) is int:
                try:
                    new_meta = int(meta)
                except ValueError:
                    new_meta = None
            elif InputPatterns.whitespace.match(meta):
                new_meta = " "
            elif tag_name == "KEXPFCCOBSCENITYRATING":
                obscenity_meta = InputPatterns.track_meta_pattern.match()
                # figure out the appropriate tag to put here (to deal with misspellings, etc)
                if obscenity_meta.group(InputPatterns.yellow):
                    new_meta = Util.Obscenity.yellow
                elif obscenity_meta.group(InputPatterns.red):
                    new_meta = Util.Obscenity.red
                elif obscenity_meta.group(InputPatterns.clean):
                    new_meta = Util.Obscenity.clean
                elif obscenity_meta.group(InputPatterns.kexp):
                    new_meta = Util.Obscenity.kexp_clean
                elif InputPatterns.whitespace.match(meta):
                    new_meta = " "
            elif tag_name == "Album Artist":
                # fill in empty track artists with entered album artist
                new_meta = meta
                self.meta_entry.track_artist_set(new_meta)
            elif tag_name == "KEXPRadioEdit":
                edit_meta = InputPatterns.radio_edit.match(meta)
                if edit_meta.group(InputPatterns.radio_edit):
                    new_meta = Util.Edits.radio_edit
                elif edit_meta.group(InputPatterns.kexp):
                    new_meta = Util.Edits.kexp_edit
                elif InputPatterns.whitespace.match(meta):
                    new_meta = " "
            else:
                new_meta = meta
        else:
            new_meta = " "

        if new_meta and not InputPatterns.whitespace.match(new_meta):
            try:
                audio_file[tag_name].value = new_meta
            except Exceptions.InvalidTagValueError:
                new_meta = " "
            audio_file[tag_name].value = old_meta

        return new_meta

    def save(self):
        # update all tracks with new metadata
        for i in range(0, len(self.tracks)):
            track = {tag.name: tag for tag in self.tracks[i]}

            for k in range(0, len(self.meta_entry.release_categories)):
                tag = self.meta_entry.release_categories[k]
                meta = self.meta_entry.release.entrycget(k, 1, 'text')
                if InputPatterns.whitespace.match(meta):
                    meta = None
                track[tag].value = meta
            for k in range(0,len(self.meta_entry.track_categories)):
                tag = self.meta_entry.track_categories[k]
                track_index = i + 1
                meta = self.meta_entry.tracks.entrycget(k, track_index, 'text')
                if InputPatterns.whitespace.match(meta):
                    meta = None
                if isinstance(track[tag].value, int):
                    meta = int(meta)
                track[tag].value = meta
            self.tracks[i].save()

    def quit(self):
        self.meta_entry.destroy()
        self.update()
        self.entry.set_focus()