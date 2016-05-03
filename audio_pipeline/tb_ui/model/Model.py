import os
from ..util import AudioFile
from ..util import Resources
from ..util import InputPatterns


not_release = -1
max_af = 2000


class ProcessDirectory(object):

    def __init__(self, root_dir):
        path, releases = os.path.split(root_dir)
        self.picard_dir = os.path.join(path, Resources.picard_directory)
        self.mbid_dir = os.path.join(path, Resources.mbid_directory)

        self.directories = list()
        for path, dirs, files in os.walk(root_dir):
            for directory in dirs:
                directory = os.path.join(path, directory)
                if self.is_release(directory):
                    self.directories.append(directory)

        self.directories.sort(key=lambda x: int(os.path.split(x)[1].split()[0]))

        self.releases = [None for directory in self.directories]

        self.current_release = None
        self.current = -1 # current directory index
        self.release = -1 # index of current release in current index (will probably mostly be 0)

        # take care of caching releases + audiofiles
        self.af = 0
        self.occupied = list()
        
        self.first()

    def first(self):
        self.current = -1
        self.release = -1
        while self.af - 20 < max_af and self.has_next():
            self.next()
            
        self.current = -1
        self.release = -1

        self.current_release = None

    def last(self):
        self.current = len(self.releases)
        self.release = -1
        while self.af - 20 < max_af and self.has_prev():
            self.prev()

        self.current = len(self.releases)
        self.release = -1
        self.current_release = None

    def next(self):
        if self.valid_release_index(self.release + 1):
            self.release += 1
        else:
            self.current += 1
            self.load_release()
            self.release = 0

        self.current_release = self.releases[self.current][self.release]
        return self.current_release

    def prev(self):
        if self.valid_release_index(self.release - 1):
            self.release -= 1
        else:
            self.current -= 1
            self.load_release()
            self.release = len(self.releases[self.current]) - 1

        self.current_release = self.releases[self.current][self.release]
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

    def load_release(self):
        if self.releases[self.current] is None:

            # get metadata for the 'current' release
            directory = self.directories[self.current]

            picard = os.path.join(self.picard_dir, os.path.split(directory)[1])
            mbid = os.path.join(self.mbid_dir, os.path.split(directory)[1])

            files = os.listdir(directory)
            indices = dict()
            releases = list()
            releases.append([])
            i = 1

            for f in files:
                file = os.path.join(directory, f)

                try:
                    file_data = AudioFile.AudioFile(file, picard, mbid)
                except IOError as e:
                    continue
                except AudioFile.UnsupportedFiletypeError as e:
                    print("Unsupported filetype")
                    continue

                if not Resources.has_mbid(file_data) and file_data.album_artist.value <= '' and file_data.album.value <= '':
                    index = 0
                else:
                    if (file_data.mbid.value, file_data.disc_num.value) in indices:
                        index = indices[(file_data.mbid.value, file_data.disc_num.value)]
                    elif (file_data.album.value, file_data.album_artist.value, file_data.disc_num.value) in indices:
                        index = indices[(file_data.album.value, file_data.album_artist.value, file_data.disc_num.value)]
                    else:
                        index = len(releases)
                        releases.append([])
                        if Resources.has_mbid(file_data):
                            indices[(file_data.mbid.value, file_data.disc_num.value)] = index
                        else:
                            indices[(file_data.album.value, file_data.album_artist.value,
                                     file_data.disc_num.value)] = index

                releases[index].append(file_data)

            if len(releases[0]) <= 0:
                releases.pop(0)

            for release in releases:
                release.sort(key=lambda x: x.track_num.value)
                self.af += len(release)

            self.releases[self.current] = releases
            self.occupied.append(self.current)
            self.set_occupied()

            self.release = 0

    def set_occupied(self):
        if self.af > max_af and len(self.occupied) > 1:
            # get rid of releases that are 'farthest away' from current release
            # releases 'in front' of the current release w/ the same distance
            # are considered closer than releases 'behind' the current release
            self.occupied.sort(key=lambda x: x - self.current if x > self.current else self.current - x + 0.5)
            while self.af > max_af and len(self.occupied) > 1:
                index = self.occupied.pop()
                release = self.releases[index]
                self.releases[index] = None
                for r in release:
                    self.af -= len(r)

    def has_next(self):
        return (self.current + 1 < len(self.releases)) or self.valid_release_index(self.release + 1)

    def has_prev(self):
        return (self.current > 0) or (self.release > 0)

    def is_release(self, directory):
        d = os.path.split(directory)[1]
        track = False
        if InputPatterns.release_pattern.match(d):
            picard = os.path.join(self.picard_dir, d)
            mbid = os.path.join(self.mbid_dir, d)

            for file in os.listdir(directory):
                file_name = os.path.join(directory, file)

                try:
                    track = AudioFile.AudioFile(file_name, os.path.join(picard, file), os.path.join(mbid, file))
                except IOError:
                    track = False
                    continue
                except AudioFile.UnsupportedFiletypeError:
                    track = False
                    continue
                break
            return track

    def valid_release_index(self, index):
        return (-1 < self.current < len(self.releases) and self.releases[self.current] is not None and
                                        0 <= index < len(self.releases[self.current]))

    def track_nums(self):
        tn = set([af.track_num.value for af in self.current_release])
        return tn