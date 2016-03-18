# Traverse a directory for audio files ripped using dBPoweramp
# Read in metadata relevant to human comparison with physical disc media info
import os
import mutagen
from util import AudioFile


class process_directory:
    def __init__(self, src_dir):
        # Create a new process_directory item, which finds all directories
        # in the specified directory (one layer)
        # and will get the relevent metadata from all audio files contained in those directories
        directories = os.listdir(src_dir)
        
        self.releases = []
        self.root = src_dir
        
        for item in directories:
            item = os.path.join(self.root, item)
            if os.path.isdir(item):
                self.releases.append(item)
        
        self.releases.sort()
        
        self.current_releases = {}
                
        if len(self.releases) > 0:
            self.cur_index = -1
        else:
            self.cur_index = None
    
    def get_next(self):
        # get index of next release
        next_release = self.cur_index
        if self.cur_index is not None and ((self.cur_index + 1) < len(self.releases)):
            for i in range(self.cur_index+1, len(self.releases)):
                files = os.listdir(self.releases[i])
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError or AudioFile.UnsupportedFiletypeError:
                        continue
                    next_release = i
                    break
                if next:
                    break
        
        meta = self.get_meta(next_release)
        return meta
        
    def get_prev(self):
        # get index of previous release
        prev_release = self.cur_index
        if self.cur_index is not None and ((self.cur_index - 1) >= 0):
            for i in reversed(range(0, self.cur_index)):
                files = os.listdir(self.releases[i])
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError or AudioFile.UnsupportedFiletypeError:
                        continue
                    prev_release = i
                    break
                if next:
                    break

        
        meta = self.get_meta(prev_release)
        return meta
            
    
    def get_meta(self, release_index):
        """
        Get the relevent metadata for the specified release
        
        :param release_index: The index of the desired directory in the directory list
        :return: List of lists of audio files. Each list corresponds to one release.
        """
        # Right now we're just gonna assume that The Info Is Good
        if release_index >= 0 and release_index < len(self.releases):
            release_dir = self.releases[release_index]
        else:
            return None
            
        if release_index != self.cur_index:
            self.cur_index = release_index
            
            files = os.listdir(release_dir)

            self.current_releases.clear()
            
            releases_index = {0: set([])}
            releases = [{}]
            i = 1
            
            for item in files:
                file = os.path.join(release_dir, item)
                try:
                    file_data = AudioFile.AudioFile(file)
                except IOError as e:
                    print("Mutagen IO error")
                    continue
                except AudioTag.UnsupportedFiletypeError as e:
                    print("Unsupported filetype")
                    continue
                # else blow up.
                
                
                # if we have no release-identifying metadata in the audio_file, put file in index 0 (general / unknown files)
                if file_data.mbid.value <= '' and file_data.album_artist.value <= '' and file_data.album.value <= '':
                   releases[0][file] = file_data
                
                else:
                    new_release = True
                    for index, release in releases_index.items():
                        if (file_data.mbid.value > '' and file_data.mbid.value in release) or \
                           (file_data.album.value in release and file_data.album_artist.value in release and \
                            file_data.release_date.value in release):
                            
                            # there's already a list of AudioFiles for this release; add file_data to that list
                            releases[index][file] = file_data
                            new_release = False
                            break
                            
                    if new_release:
                        # create a new release list & put release metadata in the release_index list
                        # to check future files
                        releases.append({file: file_data})
                        releases_index[i] = set([file_data.mbid.value, file_data.album.value, \
                                                 file_data.album_artist.value, file_data.release_date.value])
                        i += 1
                    
            self.current_releases = releases
            
        return self.current_releases
        
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

        
    def has_next(self):
        next = False
        if self.cur_index is not None and ((self.cur_index + 1) < len(self.releases)):
            for i in range(self.cur_index+1, len(self.releases)):
                files = os.listdir(self.releases[i])
                # it's not pretty, but:
                # try to create an audiofile
                # if we can make one, success!
                # if we can't, move on to the next file.
                # [also just throw away all our hard work]
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError or AudioFile.UnsupportedFiletypeError:
                        continue
                    next = True
                    break
                if next:
                    break
                    
        return next


    def has_prev(self):
        next = False
        if self.cur_index is not None and ((self.cur_index - 1) >= 0):
            for i in reversed(range(0, self.cur_index)):
                files = os.listdir(self.releases[i])
                
                for item in files:
                    file = os.path.join(self.releases[i], item)
                    try:
                        af = AudioFile.AudioFile(file)
                    except IOError or AudioFile.UnsupportedFiletypeError:
                        continue
                    next = True
                    break
                if next:
                    break

        return next