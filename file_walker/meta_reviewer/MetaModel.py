# Traverse a directory for audio files ripped using dBPoweramp
# Read in metadata relevant to human comparison with physical disc media info
import os
import mutagen
from Util import *


class process_directory:
    # TODO: Make this an iterable class, instead of a weird hacky iterable class, ya goof

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
        
        self.current_release_attributes = {}
        self.current_tracks = {}
        self.current_track_attributes = {}
        
        self.tag_normalize = MetaAttributes('attributes')
        
        if len(self.releases) > 0:
            self.cur_release = -1
        else:
            self.cur_release = None
    
    def get_next_meta(self):
    
        # get index of next release
        next_release = self.cur_release + 1
        
        meta = self.get_meta(next_release)
        return meta
        
    def get_previous_meta(self):
        # get index of previous release
        prev_release = self.cur_release - 1
        
        meta = self.get_meta(prev_release)
        return meta
            
    
    def get_meta(self, release_index):
        # Get the relevent metadata for the specified release
        # returns a tuple (release_meta, track_meta)
        # where release_meta and track_meta are both dictionaries of tag_name : tag_contents
        
        # Right now we're just gonna assume that The Info Is Good
        if release_index >= 0 and release_index < len(self.releases):
            release_dir = self.releases[release_index]
        else:
            return None, None
            
        if release_index != self.cur_release:
            self.cur_release = release_index
            
            files = os.listdir(release_dir)

            # clear out the old metadata
            self.current_release_attributes.clear()
            self.current_tracks.clear()
            self.current_track_attributes.clear()
            
            for item in files:
                # filter down to audio files we can process
                ext = os.path.splitext(item)[1]
                if ext in file_types:
                    release = {}
                    track = {}
                    track_path = os.path.join(release_dir, item)
                    
                    try:
                        raw_metadata = mutagen.File(track_path)
                    except:
                        # failed to get metadata from file -> let through incorrect filetype, file may be corrupted, whatever
                        # for now, just skip this file and continue to the next 
                        continue
                    
                    raw_length = raw_metadata.info.length
                    
                    track["length"] = minutes_seconds(raw_length)

                    if file_types[ext] == "vorbis":
                        raw_metadata = raw_metadata.tags
                        if "mbid" in raw_metadata:
                            release["release_id"] = raw_metadata["mbid"][0]
                        elif "musicbrainz_albumid" in raw_metadata:
                            release["release_id"] = raw_metadata["musicbrainz_albumid"][0]
                        if "KEXPPRIMARYGENRE" in raw_metadata:
                            track["KEXPPRIMARYGENRE"] = raw_metadata["KEXPPRIMARYGENRE"][0]
                        if "KEXPFCCOBSCENITYRATING" in raw_metadata:
                            track["KEXPFCCOBSCENITYRATING"] = raw_metadata["KEXPFCCOBSCENITYRATING"][0]
                        
                        
                        # should just have a directory of these attributes so we don't go over them one by one
                        if "album" in raw_metadata:
                            release["name"] = raw_metadata["album"][0]
                        if "albumartist" in raw_metadata:
                            release["album_artist"] = raw_metadata["albumartist"][0]   
                        if "tracknumber" in raw_metadata:
                            track["track_num"] = int(raw_metadata["tracknumber"][0])
                        if "discnumber" in raw_metadata:
                            release["disc_num"] = int(raw_metadata["discnumber"][0])
                        if "title" in raw_metadata:
                            track["name"] = raw_metadata["title"][0]
                        if "artist" in raw_metadata:
                            track["artist"] = raw_metadata["artist"][0]
                        
                    elif file_types[ext] == "aac":
                        #raw_metadata.tags._DictProxy__dict['----:com.apple.iTunes:MBID']
                        raw_metadata = raw_metadata.tags
                        if '----:com.apple.iTunes:MBID' in raw_metadata:
                            release["release_id"] = str(raw_metadata['----:com.apple.iTunes:MBID'][0])
                        elif '----:com.apple.iTunes:MusicBrainz Album Id' in raw_metadata:
                            release["release_id"] = str(raw_metadata['----:com.apple.iTunes:MusicBrainz Album Id'][0], encoding='UTF-8')
                        if '----:com.apple.iTunes:KEXPPRIMARYGENRE' in raw_metadata:
                            track["KEXPPRIMARYGENRE"] = str(raw_metadata['----:com.apple.iTunes:KEXPPRIMARYGENRE'][0], encoding='UTF-8')
                        if '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING' in raw_metadata:
                            track["KEXPFCCOBSCENITYRATING"] = str(raw_metadata['----:com.apple.iTunes:KEXPFCCOBSCENITYRATING'][0], encoding='UTF-8')
                        
                        if "\xa9alb" in raw_metadata:
                            release["name"] = str(raw_metadata["\xa9alb"][0])
                        if "\aART" in raw_metadata:
                            release["album_artist"] = str(raw_metadata["aART"][0])
                        if "disk" in raw_metadata:
                            release["disc_num"] = int(raw_metadata['disk'][0][0])
                        if 'trkn' in raw_metadata:
                            track["track_num"] = int(raw_metadata['trkn'][0][0])
                        if '\xa9nam' in raw_metadata:
                            track["name"] = str(raw_metadata['\xa9nam'][0])
                        if '\xa9ART' in raw_metadata:
                            track["artist"] = str(raw_metadata['\xa9ART'][0])

                    elif file_types[ext] == "id3":
                        raw_metadata = raw_metadata.tags
                        if 'TXXX:MBID' in raw_metadata:
                            release['release_id'] = raw_metadata['TXXX:MBID'].text[0]
                            track_num = int(raw_metadata['TRCK'].text[0].split('/')[0])
                            disc_num = int(raw_metadata['TPOS'].text[0].split('/')[0])
                        elif 'TXXX:MusicBrainz Album Id' in raw_metadata:
                            release['release_id'] = raw_metadata['TXXX:MusicBrainz Album Id'].text[0]
                            track_num = int(raw_metadata['TRCK'].text[0].split('/')[0])
                            disc_num = int(raw_metadata['TPOS'].text[0].split('/')[0])
                        if 'TXXX:KEXPPRIMARYGENRE' in raw_metadata:
                            track["KEXPPRIMARYGENRE"] = raw_metadata['TXXX:KEXPPRIMARYGENRE'].text[0]
                        if 'TXXX:KEXPFCCOBSCENITYRATING' in raw_metadata:
                            track["KEXPFCCOBSCENITYRATING"] = raw_metadata['TXXX:KEXPFCCOBSCENITYRATING'].text[0]
                            
                        if 'TALB' in raw_metadata:
                            release['name'] = raw_metadata['TALB'].text[0]
                        if "TPE1" in raw_metadata:
                            release["album_artist"] = raw_metadata["TPE1"].text[0]
                        if "TPOS" in raw_metadata:
                            release["disc_num"] = int(raw_metadata['TPOS'].text[0].split('/')[0])
                        if 'TRCK' in raw_metadata:
                            track["track_num"] = int(raw_metadata['TRCK'].text[0].split('/')[0])
                        if 'TIT2' in raw_metadata:
                            track["name"] = raw_metadata['TIT2'].text[0]
                        if 'TPE2' in raw_metadata:
                            track["artist"] = raw_metadata['TPE2'].text[0]

                    self.current_track_attributes[track_path] = track
                    self.current_release_attributes[release_dir] = release
                    self.current_tracks[track["track_num"]] = track_path

        return self.current_release_attributes, self.current_track_attributes

        
    # NEED TO ADD TAG ENCODING FOR AAC:
    #   tag_value.encode('utf-8')
    #   tag_value = mp4.MP4FreeForm(tag_value, mp4.AtomDataType.UTF8)
    #   then throw it dramatically over the wall
    
    #   also look at encoding of tag names???
        
    def update_metadata(self, file_name, new_meta):
        # Saves the key: value tags contained in new_meta
        # As (appropriately-formatted) metadata tags of the audio file specified
        try:
            audio = mutagen.File(file_name)
        except mutagen.MutagenError:
            print("Error opening " + file_name + ", tag " + new_meta + " not written.")
            return
            
        format = os.path.splitext(file_name)[1]
        if format in file_types:
            for tag_name, tag_value in new_meta.items():
                # Format the tag name for the file type / tag type
                formatted_tag = self.tag_normalize[tag_name][format]
                if formatted_tag:
                    if format in ['.m4a', '.mp4', 'aac']:
                        # (itunes-style) AAC tags must be utf-8 encoded byte strings
                        formatted_value = tag_value.encode('utf-8')
                    elif format in ['id3', '.mp3']:
                        # ID3v2.4 tags have a very specific frame structure
                        formatted_value = self.tag_normalize[tag_name]['id3_frame']
                        formatted_value.text = [tag_value]
                    else:
                        # Other tags (vorbis) are just strings
                        formatted_value = tag_value
                        
                    audio[formatted_tag] = formatted_value
                    self.current_track_attributes[file_name][tag_name] = tag_value
                    audio.save()

    def delete_metadata(self, file_name, tagnames):
        # delete the specified tag of metadata from the audio
        audio = mutagen.File(file_name)
        format = os.path.splitext(file_name)[1]
        if format in file_types:
            for tag in tagnames:
                tag_name = convert_tag(file_types[format], tag)
                if tag_name in audio.keys():
                    audio.pop(tag_name)
                    if tag in self.current_track_attributes[file_name].keys():
                        self.current_track_attributes[file_name].pop(tag)
                
        audio.save()
        
    def get_track_meta(self, file_name):
        if file_name in self.current_track_attributes.keys():
            return self.current_track_attributes[file_name]
        
    def has_next(self):
        next = False
        if self.cur_release is not None and ((self.cur_release + 1) < len(self.releases)):
            for i in range(self.cur_release+1, len(self.releases)):
                files = os.listdir(self.releases[i])
                file_exts = [os.path.splitext(item)[1] for item in files]
                for ext in file_types.keys():
                    self.cur_release = i - 1
                    if ext in file_exts:
                        next = True
                        break
                if next:
                    break
                
        return next
        
    def has_prev(self):
        next = False
        if self.cur_release is not None and ((self.cur_release - 1) >= 0):
            for i in reversed(range(0, self.cur_release)):
                files = os.listdir(self.releases[i])
                file_exts = [os.path.splitext(item)[1] for item in files]
                for ext in file_types.keys():
                    if ext in file_exts:
                        self.cur_release = i + 1
                        next = True
                        break
                if next:
                    break
            
        return next
        
def convert_tag(format, tag):
    if format is "vorbis":
        tag_name = tag.lower()
    elif format is "aac":
        tag_name = "----:com.apple.iTunes:" + tag
    elif format is 'id3':
        tag_name = "TXXX:" + tag
    else:
        tag_name = str(tag)
        
    return(tag_name)
