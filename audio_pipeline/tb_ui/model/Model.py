import os
import collections
import time
from ..util import Resources
from . import MoveFiles
from . import Rules
from . import LoadReleases


class ProcessDirectory(object):

    def __init__(self, root_dir, dest_dir, copy):
        rule = Rules.KEXPDestinationDirectoryRule(dest_dir)
        
        self.processing_complete = MoveFiles.MoveFiles(rule, copy)

        dbpoweramp = True

        starting_index = 0
        root_dir = os.path.normpath(root_dir)
        starting_dir = os.path.normpath(root_dir)

        # if len([d for d in os.listdir(root_dir) if d.is_dir()]) == 0:
        #
        #     root_dir = os.path.dirname(root_dir)

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
            print(self.directories)

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

    def set_mbid(self, mbid):
        for track in self.current_release:
            track.mbid.save(mbid)

    def move_files(self):
        self.processing_complete.move_files(self)
            
    def first(self):
        self.next_buffer.extend(self.prev_buffer)
        self.prev_buffer.clear()
            
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