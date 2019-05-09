import os
import collections
import time
from yattag import Doc

from audio_pipeline import Constants

from ..util import Resources
from . import MoveFiles
from .Rules import rules
from . import LoadReleases


class ProcessDirectory(object):

    def __init__(self, root_dir, dest_dir, copy):
        rule = rules[Constants.move_files]
        wait_for_close = Constants.wait_for_close

        if rule:
            rule = rule(dest_dir)
            self.processing_complete = MoveFiles.MoveFiles(rule, copy, wait_for_close=wait_for_close)
        else:
            self.processing_complete = None

        dbpoweramp = True

        starting_index = 0
        root_dir = os.path.normpath(root_dir)
        starting_dir = os.path.normpath(root_dir)

        if not [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]:
            root_dir = os.path.dirname(root_dir)

        self.directories = list()
        for path, dirs, files in os.walk(root_dir):
            for directory in dirs:
                directory = os.path.normpath(os.path.join(path, directory))
                if Resources.is_release(directory):
                    if dbpoweramp:
                        try:
                            int(os.path.split(directory)[1].split()[0])
                        except ValueError:
                            dbpoweramp = False
                    self.directories.append(directory)

        if dbpoweramp:
            self.directories.sort(key=lambda x: int(os.path.split(x)[1].split()[0]))
        else:
            self.directories.sort()

        if starting_dir != root_dir:
            starting_index = self.directories.index(starting_dir)

        self.__current_release = LoadReleases.CurrentReleases(self.directories)

        self.next_buffer = collections.deque()
        self.prev_buffer = collections.deque()

        self.loader_thread = LoadReleases.LoadReleases(self.prev_buffer, self.next_buffer,
                                                       self.__current_release, starting_index)
        self.loader_thread.start()

    def __del__(self):
        self.__current_release.current = None

    @property
    def current_release(self):
        if self.__current_release.current is not None:
            return self.__current_release.current[1]
        else:
            return self.__current_release.current

    def set_release_tag(self, name, value):
        for track in self.current_release:
            if name in track.release_tags:
                track.release_tags[name].value = value
                track.save()
            else:
                return False
        return True

    def get_release_seed(self, url_base):
      release_seed = MBReleaseSeed(url_base)
      release_seed.set_release_body(self.current_release[0])
      for track in self.current_release:
          release_seed.add_track(track)
      return release_seed.get_result()

    def set_mbid(self, mbid):
        release = self.loader_thread.processor.get_release(mbid)
        for track in self.current_release:
            release.stuff_audiofile(track)
            track.save()
        return "done"

    def set_discogs(self, id):
        release = self.loader_thread.processor.get_release(id, "discogs")
        for track in self.current_release:
            release.stuff_audiofile(track)
            track.save()
        return "done"

    def set_genre(self, genre):
        for track in self.current_release:
            track.secondary_genre.save(genre)

    def move_files(self):
        self.processing_complete.move_files(self)

    def first(self):
        self.next_buffer.append(self.__current_release.current)
        self.next_buffer.extend(self.prev_buffer)
        self.prev_buffer.clear()
        self.__current_release.reset()

    def next(self):
        if self.has_next():
            if self.current_release is not None:
                self.prev_buffer.append(self.__current_release.current)

            while self.has_next() and len(self.next_buffer) <= 0:
                time.sleep(.02)
                # if self.has_next() and not self.loader_thread.is_alive():
                #     print("thread died")
                #     self.loader_thread = LoadReleases.LoadReleases(self.prev_buffer, self.next_buffer,
                #                                                    self.__current_release, self.__current_release.current[0] + 1)
                #     self.loader_thread.start()
                #     print("thread revived??")

            self.__current_release.current = self.next_buffer.pop()

            return self.current_release

    def prev(self):
        if self.has_prev():
            if self.current_release is not None:
                self.next_buffer.append(self.__current_release.current)

            while self.has_prev() and len(self.prev_buffer) <= 0:
                time.sleep(.02)
                # if self.has_prev() and not self.loader_thread.is_alive():
                #     self.loader_thread = LoadReleases.LoadReleases(self.prev_buffer, self.next_buffer,
                #                                                    self.__current_release, self.__current_release.current[0] - 1)
                #     self.loader_thread.start()

            self.__current_release.current = self.prev_buffer.pop()

            return self.current_release

    def jump(self, i):
        if i < 0:
            for k in range(-1 * i):
                if self.has_prev():
                    self.prev()
        else:
            for k in range(i):
                if self.has_next():
                    self.next()

        return self.current_release

    def has_next(self):
        return len(self.next_buffer) > 0 or \
               (self.__current_release.current is not None and
                self.__current_release.current[0] < len(self.__current_release.directories) - 1)

    def has_prev(self):
        return len(self.prev_buffer) > 0 or \
               (self.__current_release.current is not None and
                self.__current_release.current[0] > 0)


    def track_nums(self):
        tn = set([af.track_num.value for af in self.current_release])
        return tn


class MBReleaseSeed:
    def __init__(self, url_base):
        """
        Class to put together an HTML form to seed the MusicBrainz add release page with metadata
        """
        self.doc, self.tag, self.text = Doc().tagtext()
        self.doc.asis('<!DOCTYPE html>')
        self.form_tag = self.tag("form", method="POST", action=url_base)
        self.form_tag.__enter__()
        self.mediums = {}

    def input_tag(self, name, value):
        if value:
            if isinstance(value, list):
                # (for now) we'll just take the first list value
                value = value[0]
            self.doc.input(name=name, value=value, type="hidden")

    def set_release_body(self, audiofile):
        # name of release
        self.input_tag("name", audiofile.album.value)
        self.input_tag("barcode", audiofile.barcode.value)
        if audiofile.release_date.value:
            # release date
            self.input_tag("events.0.date.year", audiofile.release_date.year)
            self.input_tag("events.0.date.month", audiofile.release_date.month)
            self.input_tag("events.0.date.day", audiofile.release_date.day)
        self.input_tag("events.0.country", audiofile.country.value)
        self.input_tag("type", audiofile.release_type.value)

        # label information
        self.input_tag("labels.0.name", audiofile.label.value)
        self.input_tag("labels.0.catalog_number", audiofile.catalog_num.value)

        # album artist
        # just gonna throw everything at it at once (for nooooow)
        if audiofile.album_artist.value:
            self.input_tag("artist_credit.names.0.artist.name", audiofile.album_artist.value)

    def add_track(self, audiofile):
        if audiofile.disc_num.value:
            medium = str(audiofile.disc_num.value - 1)
        else:
            medium = '0' # if there's no disc num defined, we're just gonna guess
        if medium not in self.mediums:
            medium_num = str(len(self.mediums))
            self.input_tag(".".join(("mediums", medium_num,  "format")), audiofile.media_format.value)
            self.mediums[medium] = []
        if audiofile.track_num.value not in self.mediums[medium]:
            track_num = str(len(self.mediums[medium]))
            track_base = ".".join(("mediums", medium, "track", track_num))
            self.input_tag(".".join((track_base, "name")), audiofile.title.value)
            self.input_tag(".".join((track_base, "number")), str(audiofile.track_num))
            self.input_tag(".".join((track_base, "length")), str(audiofile.length))
            artist_base = ".".join((track_base, "artist_credit", "names", "0"))
            self.input_tag(".".join((artist_base, "artist", "name")), audiofile.artist.value)
            self.mediums[medium].append(track_base)

    def get_result(self):
        # add medium position tags if necesary
        if len(self.mediums) > 1:
            for medium, tracklist in self.mediums.items():
                medium_position = ".".join(tracklist[0].split(".")[:2] + ["position"])
                self.input_tag(medium_position, medium)
        self.doc.stag("input", type="submit")
        self.form_tag.__exit__(None, None, None)
        with self.tag("script"):
          self.text("document.forms[0].submit()")

        return self.doc.getvalue()
