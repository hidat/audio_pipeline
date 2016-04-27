# Traverse a directory for audio files ripped using dBPoweramp
# Read in metadata relevant to human comparison with physical disc media info
import os
import mutagen
from ..util import AudioFile


class ProcessDirectory(object):

    def __init__(self, src_dir):
        """
        Create a new ProcessDirectory item, which will go through all subdirectories
        of the specified src_dir, find useable audio files, extract relevent metadata from
        them, and organize the audio files into releases for review.
        
        :param src_dir: Absolute path to starting directory
        """
        directories = os.listdir(src_dir)
        
        self.releases = []
        self.root = src_dir
        
        for item in directories:
            item = os.path.join(self.root, item)
            if os.path.isdir(item):
                self.releases.append(item)
        
        self.releases.sort()
        
        self.current_releases = []
        self.current_release = []
        
        self.cached = 0
        self.replace = 0
        
        self.release_index = -1
        self.cur_index = -1
    
    def get_next(self):

        if self.release_index >= 0 and self.release_index + 1 < len(self.current_releases):
            self.release_index += 1
            self.current_release = self.current_releases[self.release_index]
            return self.current_release

        # get index of next release
        next_release = None
        if self.cur_index is not None and ((self.cur_index + 1) < len(self.releases)):
            for i in range(self.cur_index+1, len(self.releases)):
                files = os.listdir(self.releases[i])
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError as e:
                        print("IOERROR " + ascii(e))
                        continue
                    except AudioFile.UnsupportedFiletypeError as e:
                        print("unsupported filetype: " + ascii(e))
                        continue
                    next_release = i
                    break
                if next_release is not None:
                    break
        
        if next_release is not None:
            meta = self.get_meta(next_release)
        else:
            meta = None
        return meta
        
    def get_prev(self):
        if 0 < self.release_index < len(self.current_releases):
            self.release_index -= 1
            self.current_release = self.current_releases[self.release_index]
            return self.current_release

        # get index of previous release
        prev_release = None
        if self.cur_index is not None and ((self.cur_index - 1) >= 0):
            for i in reversed(range(0, self.cur_index)):
                files = os.listdir(self.releases[i])
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError as e:
                        print("IOERROR " + ascii(e))
                        continue
                    except AudioFile.UnsupportedFiletypeError as e:
                        print("unsupported filetype: " + ascii(e))
                        continue
                    prev_release = i
                    break
                if prev_release is not None:
                    break

        if prev_release is not None:
            meta = self.get_meta(prev_release)
        else:
            meta = None
        return meta

    def get_meta(self, release_index):
        """
        Get the relevent metadata for the specified release
        
        :param release_index: The index of the desired directory in the directory list
        :return: List of lists of audio files. Each list corresponds to one release.
        """
        if 0 <= release_index < len(self.releases):
            release_dir = self.releases[release_index]
        else:
            return None
            
        if release_index != self.cur_index:
        
            if (len(self.current_releases) > CACHE_LIMIT):
                self.current_releases.pop(0)
        
            self.cur_index = release_index
            
            files = os.listdir(release_dir)
            
            releases_index = dict()
            releases_index[0] = set([])
            releases = [[]]
            i = 1
            
            for item in files:
                file = os.path.join(release_dir, item)
                try:
                    file_data = AudioFile.AudioFile(file)
                except IOError as e:
                    print("Mutagen IO error")
                    continue
                except AudioFile.UnsupportedFiletypeError as e:
                    print("Unsupported filetype")
                    continue
                # else blow up.

                # if we have no release-identifying metadata in the audio_file, put file in index 0 (general / unknown files)
                if file_data.mbid.value <= '' and file_data.album_artist.value <= '' and file_data.album.value <= '':
                   releases[0].append(file_data)
                
                else:
                    new_release = True
                    for index, release in releases_index.items():
                        if (file_data.mbid.value > '' and file_data.mbid.value in release and file_data.disc_num.value in release) or \
                           (file_data.album.value in release and file_data.album_artist.value in release and file_data.disc_num.value in release):
                            
                            # there's already a list of AudioFiles for this release; add file_data to that list
                            releases[index].append(file_data)
                            new_release = False
                            break
                            
                    if new_release:
                        # create a new release list & put release metadata in the release_index list
                        # to check future files
                        releases.append([file_data])
                        releases_index[i] = set([file_data.mbid.value, file_data.album.value, \
                                                 file_data.album_artist.value, file_data.disc_num.value])
                        i += 1

            if len(releases[0]) <= 0:
                releases.pop(0)

            releases = [sorted(release, key=lambda x: x.track_num.value) for release in releases]
            self.current_releases = self.current_releases + releases
            print(self.current_releases)
            self.release_index = self.release_index + 1

            self.current_release = self.current_releases[self.release_index]
            return self.current_release

    def track_nums(self):
        tracknums = set([])
        for audio_file in self.current_release:
            tracknums.add(audio_file.track_num.value)

        return tracknums

    def update_metadata(self, file_name):
        """
        Save changes to metadata of file_name
        
        :param file_name: Name of the audio file to save changes to
        :return: True on success, False on failure
        """
        # check to be sure we 'are allowed' to save changes to (are currently in directory of) this file
        success = False
        audio = None
        for release in self.current_releases:
            if file_name in release.keys():
                audio = release[file_name]
                break
                
        # Save the changes (changes are made directly to the AudioFile object by someone else)
        if audio:
            audio.save()
            success = True
            
        return success
        
    def reset(self):
        """
        Reset the model to the first album
        """
        next = None
        self.release_index = -1
        self.cur_index = -1
        
    def has_next(self):
        has_next = False
        if self.release_index >= 0 and self.release_index+1 < len(self.current_releases):
            has_next = True
        elif self.cur_index is not None and ((self.cur_index + 1) < len(self.releases)):
            for i in range(self.cur_index+1, len(self.releases)):
                files = os.listdir(self.releases[i])
                directories = []

                # it's not pretty, but:
                # try to create an audiofile
                # if we can make one, success!
                # if we can't, move on to the next file.
                # [also just throw away all our hard work]
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    if os.path.isdir(file):
                        directories.append(file)
                    else:
                        try:
                            af = AudioFile.AudioFile(file)
                        except IOError:
                            continue
                        except AudioFile.UnsupportedFiletypeError:
                            continue
                        has_next = True
                        
                new_dirs = []
                for item in directories:
                    if item not in self.releases:
                        new_dirs.append(item)
                if new_dirs > []:
                    self.releases = self.releases[0:i] + new_dirs + self.releases[i:len(self.releases)]
                if has_next:
                    break
                    
        return has_next

    def has_prev(self):
        has_next = False
        if self.release_index > 0 and self.release_index < len(self.current_releases):
            has_next = True
        elif self.cur_index is not None and ((self.cur_index - 1) >= 0):
            for i in reversed(range(0, self.cur_index)):
                files = os.listdir(self.releases[i])
                directories = []
                
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    if os.path.isdir(file):
                        directories.append(file)
                    else:
                        try:
                            af = AudioFile.AudioFile(file)
                        except IOError:
                            continue
                        except AudioFile.UnsupportedFiletypeError:
                            continue
                        has_next = True
                        
                new_dirs = []
                for item in directories:
                    if item not in self.releases:
                        new_dirs.append(item)
                if new_dirs > []:
                    self.releases = self.releases[0:i] + new_dirs + self.releases[i:len(self.releases)]
                if has_next:
                    break

        return has_next
        
