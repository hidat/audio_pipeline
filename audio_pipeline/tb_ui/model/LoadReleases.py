import threading
import os
import time
from audio_pipeline.util import AcoustidLookup as lookup
from ...util.AudioFileFactory import AudioFileFactory
from ..util import Resources
from ...util import Exceptions

MAX_RELEASES = 30


class LoadReleases(threading.Thread):

    fuzz = 3

    def __init__(self, prev_buffer, next_buffer, current_release, max_releases=MAX_RELEASES):
        """
        Load next releases
        """
        threading.Thread.__init__(self)
        self.prev_buffer = prev_buffer
        self.next_buffer = next_buffer
        self.max_buffer = max_releases
        self.current_release = current_release
        self.loaded = 0
        
        # make sure there are two releases pre-loaded
        for i in range(self.fuzz):
            self.load_release(self.next_buffer, i)
            self.loaded += 1

    def run(self):
        time.sleep(.1)
        
        num_dirs = len(self.current_release.directories)
        
        next_limit = num_dirs - self.max_buffer
        prev_limit = self.max_buffer
        
        while self.current_release.current is not None and self.loaded < num_dirs:

            # if buffers are full, wait for a signal from the model proper to load more releases,
            # rather than constantly looping and wasting resources
            
            self.current_release.cond.acquire()
            if len(self.next_buffer) >= self.max_buffer + self.fuzz:
                self.trim_releases(self.next_buffer)
            elif len(self.next_buffer) < self.max_buffer and \
                 (next_limit < 0 or self.current_release.current[0] < next_limit):
                print("loading next")
                # haven't filled in next_buffer / have moved forward
                # get next value
                last_release = self.next_buffer.popleft()
                self.next_buffer.appendleft(last_release)

                i = last_release[0] + 1
                self.current_release.cond.release()
                self.load_release(self.next_buffer, i)
                self.current_release.cond.acquire()
                self.loaded += 1

            if len(self.prev_buffer) >= self.max_buffer + self.fuzz:
                self.trim_releases(self.prev_buffer)
            elif len(self.prev_buffer) < self.max_buffer and \
                 self.current_release.current[0] > self.max_buffer:
                print("loading prev")
                # haven't filled in prev_buffer / have moved forward
                # so get next buffer
                last_release = self.prev_buffer.popleft()
                self.prev_buffer.appendleft(last_release)

                i = last_release[0] - 1
                self.current_release.cond.release()
                self.load_release(self.prev_buffer, i)
                self.current_release.cond.acquire()
                self.loaded += 1
                
                
            while (len(self.next_buffer) >= self.max_buffer or \
                (next_limit > 0 and self.current_release.current[0] >= next_limit)) and \
                (len(self.prev_buffer) >= self.max_buffer or \
                    self.current_release.current[0] <= prev_limit) or \
                 self.loaded % 7 == 0:
                 
                print("waiting (for a miracle)")
                self.current_release.cond.wait()
                
                if self.current_release.current is None or self.loaded % 7 == 0:
                    break
            self.current_release.cond.release()


            
        print("Loaded: " + str(self.loaded))
        print("Number of directories: " + str(len(self.current_release.directories)))
        print("Maximum loaded releases: " + str(self.max_buffer))

        
    def trim_releases(self, buffer):
        # remove releases from the end of the buffer,
        # preventing the removal of partial directories.
        print("trimming release????")
        last_directory = list()
        last_release = buffer.popleft()
        last_directory.append(last_release)
        
        index = last_release[0]
        last_release = buffer.popleft()

        while index == last_release[0] and len(buffer) >= self.max_buffer + (self.fuzz / 2):
            last_directory.append(last_release)
            last_release = buffer.popleft()
            
        buffer.appendleft(last_release)

        if len(buffer) < self.max_buffer + (self.fuzz / 2):
            # don't want some sort of 50-release directory getting constantly deleted and reloaded
            buffer.extendleft(last_directory)
        else:
            self.loaded -= len(last_directory)
                        
    def load_release(self, buffer, dir_index):
        if len(buffer) >= self.max_buffer:
            return None
            
        directory = self.current_release.directories[dir_index]

        files = os.listdir(directory)
        indices = dict()
        releases = list()
        releases.append([])
        i = 1

        for f in files:
            file = os.path.join(directory, f)

            try:
                file_data = AudioFileFactory.get(file)
            except IOError as e:
                continue
            except Exceptions.UnsupportedFiletypeError as e:
                print("Unsupported filetype")
                continue

            if not Resources.has_mbid(file_data) and file_data.album_artist.value is None and file_data.album.value is None:
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
        else:
            lookup.Release(releases[0]).stuff_meta()
            
        for release in releases:
            release.sort(key=lambda x: x.track_num.value if x.track_num.value is not None else 0)
            buffer.appendleft((dir_index, release))

            
class CurrentReleases:

    def __init__(self, directories, timeout=.01):
        self.directories = directories
        self.__current = (None, None)
        self.__prev = (None, None)
        self.cond = threading.Condition()
        
    @property
    def current(self):
        self.cond.acquire()
        v = self.__current
        self.cond.notify()
        self.cond.release()
        return v
                
    @current.setter
    def current(self, value):
        self.cond.acquire()
        self.__current = value
        self.cond.notify()
        self.cond.release()
        
    @property
    def prev(self):
        self.__cond.acquire()
        v = self.__prev
        self.__cond.notify()
        self.__cond.release()
        return v
        
    @prev.setter
    def prev(self, value):
        self.cond.acquire()
        self.prev = value
        self.cond.notify()
        self.cond.release()
