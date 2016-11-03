import threading
import os
import time
from audio_pipeline.util import AcoustidLookup as lookup
from audio_pipeline.util import Process
from audio_pipeline.util import Util
from audio_pipeline.util.MusicBrainz import PreferredRelease
from audio_pipeline import Constants
from ..util import InputPatterns
from ...util.AudioFileFactory import AudioFileFactory
from ..util import Resources
from ...util import Exceptions

MAX_RELEASES = 500
MATCHING_RATIO = .75
FEW_TRACKS = 3
WRONG_SINGLE = .4


class LoadReleases(threading.Thread):

    fuzz = 3

    def __init__(self, prev_buffer, next_buffer, current_release, starting_index=0, max_releases=MAX_RELEASES):
        """
        Load next releases
        """
        threading.Thread.__init__(self)
        self.prev_buffer = prev_buffer
        self.next_buffer = next_buffer
        self.max_buffer = max_releases
        self.starting_index = starting_index
        self.current_release = current_release
        self.loaded = 0
        self.scanned = 0
        self.processor = Process.Processor(Constants.processor, Constants.batch_constants.mb)
        self.lookup = Constants.load_releases

    def run(self):
        time.sleep(.1)
        
        num_dirs = len(self.current_release.directories)

        if self.starting_index != 0:
            self.load_release(self.next_buffer, self.starting_index, self.lookup)
            self.loaded += 1
            self.starting_index += 1

        while self.current_release.current is not None and self.loaded < num_dirs and self.loaded < self.max_buffer:

            # if buffers are full, wait for a signal from the model proper to load more releases,
            # rather than constantly looping and wasting resources
            
            self.current_release.cond.acquire()
            if self.current_release.current is not None and \
                            len(self.next_buffer) + self.current_release.current[0] < num_dirs:
                # haven't filled in next_buffer / have moved forward
                # get next value
                if len(self.next_buffer) > 0:
                    last_release = self.next_buffer[0]
                else:
                    last_release = self.current_release.current

                i = last_release[0] + 1
                if i < num_dirs:
                    print("loading next " + str(i))
                    self.current_release.cond.release()
                    self.load_release(self.next_buffer, i, self.lookup)
                    self.current_release.cond.acquire()
                    self.loaded += 1

            if self.current_release.current is not None and \
                            len(self.prev_buffer) <= self.current_release.current[0]:
                # haven't filled in prev_buffer / have moved forward
                # so get next buffer
                if len(self.prev_buffer) > 0:
                    last_release = self.prev_buffer[0]
                else:
                    last_release = self.current_release.current

                i = last_release[0] - 1
                if i >= 0:
                    print("loading prev " + str(i))
                    self.current_release.cond.release()
                    self.load_release(self.prev_buffer, i, self.lookup)
                    self.current_release.cond.acquire()
                    self.loaded += 1
                
            self.current_release.cond.release()

        print("Loaded: " + str(self.loaded))
        print("All releases loaded")

    def load_release(self, buffer, dir_index, scan=True):
        if len(buffer) >= self.max_buffer:
            return None
            
        directory = self.current_release.directories[dir_index]

        files = os.listdir(directory)
        indices = dict()
        to_scan = set()
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

            if not Resources.has_mbid(file_data) and \
                    (InputPatterns.unknown_artist.match(str(file_data.album_artist))) and \
                    not str(file_data.album_artist):
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
                    to_scan.add(index)

            releases[index].append(file_data)

            # all releases are initially added to the to_scan pile; if they should not be
            # (already scanned, already had metadata stuffed, have mbid & have more tracks
            # than our 'confidence threshold') remove them
            if (file_data.acoustid.value or file_data.meta_stuffed.value or \
                    (Resources.has_mbid(file_data) and len(releases[index]) > FEW_TRACKS)) \
                    and index in to_scan:
                to_scan.remove(index)

        if scan:
            for i in to_scan:
                r = lookup.Release(releases[i])
                r.lookup()
                if r.best_group:
                    p = PreferredRelease.BestRelease(r)

                    if len(releases[i]) <= FEW_TRACKS:
                        p.choose_release()
                        p.set_mbid(p.best_release)
                        self.scanned += 1
                    else:
                        match = p.mb_comparison(True)
                        print(match)
                        if match is not None and (match > MATCHING_RATIO):
                            p.set_mbid(p.best_release)
                            self.scanned += 1

        if len(releases[0]) <= 0:
            releases.pop(0)
        else:
            if scan:
                p = PreferredRelease.BestRelease(lookup.Release(releases[0]))
                p.choose_release()
                p.set_mbid(p.best_release)
                self.scanned += 1

        for release in releases:

            if scan and (Util.has_mbid(release[0]) and not release[0].meta_stuffed.value):
                release_meta = self.processor.get_release(release[0].mbid.value)
                meta = release_meta.release
                # stuff any additional MB metadata
                for track in release:
                    if track.meta_stuffed.value:
                        continue
                    track.stuff_release(meta)
                    track.meta_stuffed.value = "yep"
                    if meta.disc_count is None:
                        track.mbid.value = None
                        pass
                    elif track.disc_num.value <= meta.disc_count:
                        track_meta = release_meta.get_track(track)
                        # need to create new processor w/ no item_code save - for now, just kill it here.
                        track.title.value = track_meta.title
                        if track_meta.artist_phrase:
                            track.artist.value = track_meta.artist_phrase
                        else:
                            track.artist.value = track_meta.artist_credit
                    else:
                        track.artist.value = meta.artist
                        track.title.value = ""

                    track.item_code.value = None
                    track.save()

            release.sort(key=lambda x: x.track_num.value if x.track_num.value is not None else 0)
            buffer.appendleft((dir_index, release))


class CurrentReleases:

    def __init__(self, directories, timeout=.01):
        self.directories = directories
        self.__current = (-1, None)
        self.__prev = (-1, None)
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
        self.cond.acquire()
        v = self.__prev
        self.cond.notify()
        self.cond.release()
        return v
        
    @prev.setter
    def prev(self, value):
        self.cond.acquire()
        self.prev = value
        self.cond.notify()
        self.cond.release()
