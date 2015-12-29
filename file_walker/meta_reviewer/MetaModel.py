# Traverse a directory for audio files ripped using dBPoweramp
# Read in metadata relevant to human comparison with physical disc media info
import os
import mutagen
from Util import *


def class process_directory:

    def __init__(self, src_dir):
        # walk the source directory for child directories, each of which is a ripped disc
        directories = self.listdir(src_dir)
        
        self.releases = {}
        self.root = src_dir
        
        for item in directories:
            if item.is_dir():
                self.releases.append(item)
        
        self.releases.sort()
        self.releases.reverse()
        
        self.cur_release = self.releases.pop()
        
    def get_meta():
        # Get the relevant metadata of the current release and iterate to the next release
        # returns a tuple (release_meta, track_meta)
        # where release_meta and track_meta are both dictionaries of tag_name : tag_contents
        
        release_dir = os.path.join(self.root, self.cur_release)
        
        # Get next release
        if (len(self.cur_release) > 0):
            self.cur_release = self.releases.pop()
            
        files = os.listdir(release_dir)
        tracks = []
        for item in files:
            # filter down to audio files we can process
            ext = os.path.splitext(item)[1]
            if ext in file_types:
                track_path = os.path.join(release_dir, item)
                
                raw_metadata = mutagen.Files(track_path)
                
                if file_types[ext] == "vorbis":
                    if "mbid" in raw_metadata:
                        release_id = raw_metadata["mbid"][0]
                    elif "musicbrainz_albumid" in raw_metadata:
                        release_id = raw_metadata["musicbrainz_albumid"][0]
                    if "KEXPPRIMARYGENRE" in raw_metadata:
                        kexp_category = raw_metadata["KEXPPRIMARYGENRE"][0]
                    if "KEXPFCCOBSCENITYRATING" in raw_metadata:
                        kexp_obscenity_rating = raw_metadata["KEXPFCCOBSCENITYRATING"][0]
                        
                    track_num = int(raw_metadata["tracknumber"][0]) - 1
                    disc_num = int(raw_metadata["discnumber"][0])
                    

                elif file_types[ext] == "aac":
                    #raw_metadata.tags._DictProxy__dict['----:com.apple.iTunes:MBID']
                    raw_metadata = raw_metadata.tags
                    if '----:com.apple.iTunes:MBID' in raw_metadata:
                        release_id = str(raw_metadata['----:com.apple.iTunes:MBID'][0])
                    elif '----:com.apple.iTunes:MusicBrainz Album Id' in raw_metadata:
                        release_id = str(raw_metadata['----:com.apple.iTunes:MusicBrainz Album Id'][0], encoding='UTF-8')
                    if '----:com.apple.iTunes:KEXPPRIMARYGENRE' in raw_metadata:
                        kexp_category = str(raw_metadata['----:com.apple.iTunes:KEXPPRIMARYGENRE'][0], encoding='UTF-8')
                    if '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING' in raw_metadata:
                        kexp_obscenity_rating = str(raw_metadata['----:com.apple.iTunes:KEXPFCCOBSCENITYRATING'][0], encoding='UTF-8')
                        
                    track_num = int(raw_metadata['trkn'][0][0]) - 1
                    disc_num = int(raw_metadata['disk'][0][0])


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
                        kexp_category = raw_metadata['TXXX:KEXPPRIMARYGENRE'].text[0]
                    if 'TXXX:KEXPFCCOBSCENITYRATING' in raw_metadata:
                        kexp_obscenity_rating = raw_metadata['TXXX:KEXPFCCOBSCENITYRATING'].text[0]
                   

    def update_metadata(file_name, new_meta):
        # save the passed metadata to the specified filename
        
    def has_next():
        next = False
        
        if len(self.releases) > 0:
            next = True
        else:
            next = False
            
        return next
