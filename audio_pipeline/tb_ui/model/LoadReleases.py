import threading
import os
import time
from ...util.AudioFileFactory import AudioFileFactory
from ..util import Resources
from ..util import InputPatterns
from ...util import Exceptions

MAX_RELEASES = 20


class LoadReleases(threading.Thread):

    def __init__(self, prev_buffer, next_buffer, current_release, max_releases=MAX_RELEASES):
        """
        Load next releases
        """
        threading.Thread.__init__(self)
        self.prev_buffer = prev_buffer
        self.next_buffer = next_buffer
        self.max_buffer = max_releases
        self.current_release = current_release
        
        # make sure there are two releases pre-loaded
        for i in range(5):
            self.load_release(self.next_buffer, i)
        
    def run(self):
        buffered_length = len(self.next_buffer) + len(self.prev_buffer)
        while buffered_length < len(self.current_release.directories):
                       
            if len(self.next_buffer) < self.max_buffer and buffered_length < len(self.current_release.directories):
                # haven't filled in next_buffer / have moved forward
                # get next value
                last_release = self.next_buffer.popleft()
                self.next_buffer.appendleft(last_release)
                    
                i = last_release[0] + 1
                self.load_release(self.next_buffer, i)
                
            buffered_length = len(self.next_buffer) + len(self.prev_buffer)
                
                # prev_release = self.current_release.prev
                # if prev_release is not None:
                #    self.prev_buffer.append(prev_release)
            # if len(self.prev_buffer) < self.max_buffer:
                # haven't filled in buffer / have moved backwards
                # get next value
                # if len(self.prev_buffer) > 0:
                    # last_release = self.prev_buffer.popleft()
                    # self.prev_buffer.appendleft(last_release)
                
                # next_release = self.current_release.prev
                # if next_release is not None:
                    # self.next_buffer.append(next_release)
                    
                # i = last_release -= 1
                # self.load_release(self.prev_buffer, i)
                        
    def load_release(self, buffer, index):
        if len(buffer) >= self.max_buffer:
            return None
            
        directory = self.current_release.directories[index]

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

        for release in releases:
            release.sort(key=lambda x: x.track_num.value if x.track_num.value is not None else 0)
            buffer.append((index, release))

            
class CurrentReleases:

    def __init__(self, directories, timeout=.01):
        self.directories = directories
        self.__current = (None, None)
        self.__prev = (None, None)
        self.__cond = threading.Condition()
        
    @property
    def current(self):
        self.__cond.acquire()
        v = self.__current
        self.__cond.notify()
        self.__cond.release()
        return v
                
    @current.setter
    def current(self, value):
        self.__cond.acquire()
        self.__current = value
        self.__cond.notify()
        self.__cond.release()
        
    @property
    def prev(self):
        self.__cond.acquire()
        v = self.__prev
        self.__cond.notify()
        self.__cond.release()
        return v
        
    @prev.setter
    def prev(self, value):
        self.__cond.acquire()
        self.__prev = value
        self.__cond.notify()
        self.__cond.release()
