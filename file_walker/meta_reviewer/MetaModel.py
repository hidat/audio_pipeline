# Traverse a directory for audio files ripped using dBPoweramp
# Read in metadata relevant to human comparison with physical disc media info
import os
import mutagen
from Util import *


class process_directory:

    def __init__(self, src_dir):
        # walk the source directory for child directories, each of which is a ripped disc
        directories = os.listdir(src_dir)
        
        self.releases = []
        self.root = src_dir
        
        for item in directories:
            self.releases.append(item)
        
        self.releases.sort()
        self.releases.reverse()
        
        self.cur_release = self.releases.pop()
    
    def get_next_meta(self):
        print('asdf')
        
    def get_last_meta(self):
        print('asd')
    
    def get_meta(self):
        # Get the relevant metadata of the current release and iterate to the next release
        # returns a tuple (release_meta, track_meta)
        # where release_meta and track_meta are both dictionaries of tag_name : tag_contents
        
        # Right now we're just gonna assume that The Info Is Good
        
        release_dir = os.path.join(self.root, self.cur_release)
        
        # Get next release
        if (len(self.cur_release) > 0):
            self.cur_release = self.releases.pop()
            
        files = os.listdir(release_dir)
        # list of release metadata
        release_data = {}
        track_data = {}
        for item in files:
            # filter down to audio files we can process
            ext = os.path.splitext(item)[1]
            if ext in file_types:
                track_path = os.path.join(release_dir, item)
                
                raw_metadata = mutagen.File(track_path)
                                        
                release = {}
                track = {}
                
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

                # id3 is currently not supported by meta_reviewer
                elif file_types[ext] == "id3":
                    raw_metadata = raw_metadata.tags
                    if 'TXXX:MBID' in raw_metadata:
                        release_id = raw_metadata['TXXX:MBID'].text[0]
                        track_num = int(raw_metadata['TRCK'].text[0].split('/')[0]) - 1
                        disc_num = int(raw_metadata['TPOS'].text[0].split('/')[0])
                    elif 'TXXX:MusicBrainz Album Id' in raw_metadata:
                        release_id = raw_metadata['TXXX:MusicBrainz Album Id'].text[0]
                        track_num = int(raw_metadata['TRCK'].text[0].split('/')[0]) - 1
                        disc_num = int(raw_metadata['TPOS'].text[0].split('/')[0])
                    if 'TXXX:KEXPPRIMARYGENRE' in raw_metadata:
                        track["KEXPPRIMARYGENRE"] = raw_metadata['TXXX:KEXPPRIMARYGENRE'].text[0]
                    if 'TXXX:KEXPFCCOBSCENITYRATING' in raw_metadata:
                        track["KEXPFCCOBSCENITYRATING"] = raw_metadata['TXXX:KEXPFCCOBSCENITYRATING'].text[0]
                        
                track_data[track_path] = track
                release_data[release_dir] = release
        
        return release_data, track_data

    def update_metadata(self, file_name, new_meta):
        # saves the key: value tags contained in new_meta
        # as metadata tags of the audio file
        audio = mutagen.File(file_name)
        for tag_name, tag_value in new_meta.items():
            # check if this tag is already in the metadata
            # if it is, just overwrite it?
            audio[str(tag_name)] = tag_value
            audio.save()
        
    def has_next(self):
        next = False
        
        if len(self.releases) > 0:
            next = True
        else:
            next = False
            
        return next
