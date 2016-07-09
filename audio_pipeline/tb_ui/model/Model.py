import os
import collections
from ..model import MoveFiles
from ...util.AudioFileFactory import AudioFileFactory
from ..util import Resources
from ..util import InputPatterns
from ...util import Exceptions
from . import Rules
from . import LoadReleases

max_af = 700

max_queued = 20

class ProcessDirectory(object):

    def __init__(self, root_dir, dest_dir, copy):
        rule = Rules.KEXPDestinationDirectoryRule(dest_dir)
        
        self.processing_complete = MoveFiles.MoveFiles(rule, copy)

        dbpoweramp = True

        self.directories = list()
        for path, dirs, files in os.walk(root_dir):
            for directory in dirs:
                directory = os.path.join(path, directory)
                if self.is_release(directory):
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

        self.releases = [None for directory in self.directories]

        self.__current_release = None
        self.current = -1 # current directory index
        self.release = -1 # index of current release in current index (will probably mostly be 0)

        self.release_info = LoadReleases.CurrentReleases(self.directories)
        
        self.next_buffer = collections.deque()
        self.prev_buffer = collections.deque()
        
        LoadReleases.LoadReleases(self.prev_buffer, self.next_buffer, self.release_info).start()

    @property
    def current_release(self):
        if self.__current_release:
            return self.__current_release[1]
        else:
            return self.__current_release
            
    def first(self):
        self.next_buffer.extend(self.prev_buffer)
        self.prev_buffer.clear()
            
    def next(self):
        self.prev_buffer.append(self.__current_release)
        self.__current_release = self.next_buffer.pop()
        self.release_info.current = self.__current_release
        
        print(len(self.next_buffer))
        print(len(self.prev_buffer))
        
        return self.current_release

    def prev(self):
        self.next_buffer.append(self.__current_release)
        self.__current_release = self.prev_buffer.pop()
        self.release_info.current = self.__current_release
        
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
        return len(self.next_buffer) != 0

    def has_prev(self):
        return len(self.prev_buffer) != 0

    @staticmethod
    def is_release(directory):
        d = os.path.split(directory)[1]
        track = False
        # we'll set this to a DBPOWERAMP config later

        #if InputPatterns.release_pattern.match(d):

        for f in os.scandir(directory):
            if f.is_file:
                file_name = f.name

                try:
                    track = AudioFileFactory.get(f.path)
                except IOError:
                    track = False
                    continue
                except Exceptions.UnsupportedFiletypeError:
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