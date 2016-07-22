import os
import collections
import time
from ..model import MoveFiles
from ...util.AudioFileFactory import AudioFileFactory
from ...util import Exceptions
from . import Rules
from . import LoadReleases


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
        
        self.__current_release = LoadReleases.CurrentReleases(self.directories)
                
        self.next_buffer = collections.deque()
        self.prev_buffer = collections.deque()
        
        LoadReleases.LoadReleases(self.prev_buffer, self.next_buffer, self.__current_release).start()

    def __del__(self):
        self.__current_release.current = None
        
    @property
    def current_release(self):
        if self.__current_release.current is not None:
            return self.__current_release.current[1]
        else:
            return self.__current_release.current
            
    def move_files(self):
        self.processing_complete.move_files(self)
            
    def first(self):
        self.next_buffer.extend(self.prev_buffer)
        self.prev_buffer.clear()
            
    def next(self):
        if self.current_release is not None:
            self.prev_buffer.append(self.__current_release.current)

        while len(self.next_buffer) <= 0:
            time.sleep(.02)
            print("waiting: " + str(len(self.next_buffer)))
        self.__current_release.current = self.next_buffer.pop()

        return self.current_release

    def prev(self):
        if self.current_release is not None:
            self.next_buffer.append(self.__current_release.current)

        while len(self.prev_buffer) <= 0:
            time.sleep(.02)
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
        return len(self.next_buffer) > 0 or self.__current_release.current[0] < len(self.__current_release.directories) - 1

    def has_prev(self):
        return len(self.prev_buffer) > 0 or self.__current_release.current[0] > 0

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

    def track_nums(self):
        tn = set([af.track_num.value for af in self.current_release])
        return tn