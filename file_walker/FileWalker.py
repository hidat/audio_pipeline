__author__ = 'cephalopodblue'
import os
import MBInfo
import MetaProcessor
import argparse
import mutagen
import shutil
import JsonSerializer
import DaletSerializer
import csv
import hashlib
import uuid as UUID
import sys
import datetime

_file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis", "ERROR_EXT": "ERROR_EXT"}


def process_directory(source_dir, output_dir, batch_meta, generate, serializer, delete_processed):
    cached_mb_releases = {}
    unique_artists = {}
    unique_labels = set([])
    current_release_id = ''
    
    # Get location of metadata files
    track_meta_dir, artist_meta_dir, release_meta_dir = meta_directories(output_dir)
    
    # If copying audio (not just generating metadata), 
    # get the locations that audio files will be copied to
    if not generate:
        track_dir, track_success_dir, track_fail_dir = audio_directories(output_dir)
    
    # Get directories for log files & processed hashes
    processed_hashes, log_dir = info_directories(output_dir)

    # set up current log file
    date_time = datetime.datetime
    ts = date_time.now()
    # create & open log file
    log_file_name = os.path.join(log_dir, ts.strftime("filewalker_log_%d-%m-%y-%H%M%S%f.txt"))
    
    path_start = len(source_dir) + 1
    for root, dir, files in os.walk(source_dir):
        if len(root) > path_start:
            path = root[path_start:]
        else:
            path = ''
        print(ascii(path))
        for src_name in files:
            file_name = os.path.join(root, src_name)
            copy_to_path = ''
            ext = os.path.splitext(file_name)[1].lower()
            
            if ext in _file_types:
                # check if file is in processed_hash directory
                sha1 = hashlib.sha1()
                with open(file_name, 'rb') as f:
                    sha1.update(f.read())
                
                hash_file = os.path.join(processed_hashes, sha1.hexdigest())
                
                if not os.path.exists(hash_file):
                    # Get the MusicBrainz Release ID from the file
                    try:
                        raw_metadata = mutagen.File(file_name)
                    except IOError:
                        print("Error reading file {0}".format(ascii(file_name)))
                        if not generate:
                            copy_to_path = os.path.join(track_fail_dir, path)
                        ext = "ERROR_EXT"
                    
                    release_id, track_num, disc_num, kexp_obscenity_rating, kexp_category =\
                        get_mutagen_meta(raw_metadata, ext)

                    if release_id > '':
                                        
                        # open log file for writing log data
                        # currently the log file will be littered with duplicate tracks
                        log_file = open(log_file_name, 'ab')
                    
                        print("Processing " + ascii(file_name))
                        try:
                            #See if we have already cached the release, or we need to pull if from MusicBrainz
                            if release_id in cached_mb_releases:
                                mb_release = cached_mb_releases[release_id]
                                release = MetaProcessor.process_release(mb_release)
                            else:
                                # pull and cache release metadata
                                mb_release = MBInfo.get_release(release_id)
                                cached_mb_releases[release_id] = mb_release
                                release = MetaProcessor.process_release(mb_release)
                                # save release meta
                                serializer.save_release(release, batch_meta, release_meta_dir)
                                # save release to log
                                log_file.write(release["log_text"].encode("UTF-8"))
                                for label in release["labels"]:
                                    if 'label' in label:
                                        label_log = "label\t" + str(label['label']['id']) + "\t" + str(label['label']['name']) + "\r\n"
                                        log_file.write(label_log.encode("UTF-8"))
                            
                            # Pull metadata from MusicBrainz
                            track_data = MetaProcessor.process_track(mb_release, batch_meta, disc_num, track_num)
                            
                            # Add KEXP added metadata from tags
                            track_data['kexp_category'] = kexp_category
                            track_data['kexp_obscenity_rating'] = kexp_obscenity_rating
                            
                            # If this is a radio edit, assign a unique track id so we can also have a non-radio edit with the same MBID
                            if kexp_obscenity_rating.upper() == "RADIO EDIT":
                                item_code = str(UUID.uuid4())
                                track_type = str("track-with-filewalker-GUID")
                            else:
                                item_code = track_data["release_track_id"]
                                track_type = str("track")

                            track_data["item_code"] = item_code

                            # Save track info to log file
                            track_log = track_type + "\t" + str(track_data["item_code"]) + "\t" + str(track_data["title"]) + "\r\n"
                            log_file.write(track_log.encode("UTF-8"))
                                
                            # Save the track metadata
                            serializer.save_track(release, track_data, batch_meta, track_meta_dir)

                            # Copy files to to success directory
                            # target = os.path.join(track_dir, track_data["item_code"] + ext)
                            # shutil.copy(file_name, target)

                            # Make a backup of original file just in case
                            if not generate:
                                copy_to_path = os.path.join(track_success_dir, path)                            
                        
                            # Add any new artist to our unique artists list
                            for artist in track_data["artist-credit"]:
                                if 'artist' in artist:
                                    a = artist['artist']
                                    artist_id = a['id']
                                    if not (artist_id in unique_artists):
                                        artist_meta = MBInfo.get_artist(artist_id)
                                        unique_artists[artist_id] = artist_meta['title']
                                        artist_members = []
                                        if "artist-relation-list" in artist_meta:
                                            for member in artist_meta["artist-relation-list"]:
                                                member_id = member["artist"]["id"]
                                                if not (member_id in unique_artists):
                                                    if member["type"] == 'member of band' and 'direction' in member \
                                                            and member["direction"] == "backward":
                                                        unique_artists[member_id] = member["artist"]["name"]
                                                        artist_members.append(MBInfo.get_artist(member_id))
                                        
                                        # add artist to log file
                                        log = artist_meta["log_text"]
                                        log_file.write(log.encode("UTF-8"))
                                        for member in artist_members:
                                            log_file.write(member["log_text"].encode("UTF-8"))
                                        serializer.save_artist(artist_meta, artist_members, artist_meta_dir)

                        except UnicodeDecodeError:
                            print("    ERROR: Invalid characters!")
                        log_file.close()
                    else:
                        print("Skipping " + ascii(file_name))
                        if not generate:
                            copy_to_path = os.path.join(track_fail_dir, path)

                    # Move the file out of the source directory
                    if copy_to_path > '':
                        # copy files to success directory
                        target = os.path.join(track_dir, track_data["item_code"] + ext)
                        shutil.copy(file_name, target)
                    
                        # make backup of original file just in case
                        if not os.path.exists(copy_to_path):
                            os.makedirs(copy_to_path)
                        target = os.path.join(copy_to_path, src_name)
                        if delete_processed:
                            shutil.move(file_name, target)
                        else:
                            shutil.copy(file_name, target)

                    with open(hash_file, 'w+') as hash_file_d:
                        hash_file_d.write(ascii(file_name))
                        
                        
def meta_directories(output_dir):
    track_meta_dir = os.path.join(output_dir, 'track_meta')
    if not os.path.exists(track_meta_dir):
        os.makedirs(track_meta_dir)
    artist_meta_dir = os.path.join(output_dir, 'artist_meta')
    if not os.path.exists(artist_meta_dir):
        os.makedirs(artist_meta_dir)
    release_meta_dir = os.path.join(output_dir, 'release_meta')
    if not os.path.exists(release_meta_dir):
        os.makedirs(release_meta_dir)
        
    return track_meta_dir, artist_meta_dir, release_meta_dir


def audio_directories(output_dir):
    track_dir = os.path.join(output_dir, 'track')
    if not os.path.exists(track_dir):
        os.makedirs(track_dir)

    track_success_dir = os.path.join(output_dir, 'found')
    if not os.path.exists(track_success_dir):
        os.makedirs(track_success_dir)
    print("Track Success: ", track_success_dir)

    track_fail_dir = os.path.join(output_dir, 'not_found')
    if not os.path.exists(track_fail_dir):
        os.makedirs(track_fail_dir)
    print("Track Fail: ", track_fail_dir)
    
    return track_dir, track_success_dir, track_fail_dir
    
    
def info_directories(output_dir):
    # get directories where we put 'extra' info - i.e. log files & hash files
    processed_hashes = os.path.join(output_dir, 'processed_hashes')
    if not os.path.exists(processed_hashes):
        os.makedirs(processed_hashes)
        
    log_dir = os.path.join(output_dir, 'session_logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    print("Logs: ", log_dir)
    
    return processed_hashes, log_dir

    
def get_mutagen_meta(raw_metadata, ext):
    # get the relavent metadata from the raw metadata extracted by mutagen
    release_id = ''
    kexp_obscenity_rating = ''
    kexp_category = ''
    track_num, disc_num = 0, 0

    if _file_types[ext] == "vorbis":
        if "mbid" in raw_metadata:
            release_id = raw_metadata["mbid"][0]
            track_num = int(raw_metadata["tracknumber"][0]) - 1
            disc_num = int(raw_metadata["discnumber"][0])
        elif "musicbrainz_albumid" in raw_metadata:
            release_id = raw_metadata["musicbrainz_albumid"][0]
            track_num = int(raw_metadata["tracknumber"][0]) - 1
            disc_num =  int(raw_metadata["discnumber"][0])
        if "KEXPPRIMARYGENRE" in raw_metadata:
            kexp_category = raw_metadata["KEXPPRIMARYGENRE"][0]
        if "KEXPFCCOBSCENITYRATING" in raw_metadata:
            kexp_obscenity_rating = raw_metadata["KEXPFCCOBSCENITYRATING"][0]

    elif _file_types[ext] == "aac":
        #raw_metadata.tags._DictProxy__dict['----:com.apple.iTunes:MBID']
        raw_metadata = raw_metadata.tags._DictProxy__dict
        if '----:com.apple.iTunes:MBID' in raw_metadata:
            release_id = str(raw_metadata['----:com.apple.iTunes:MBID'][0])
            track_num = int(raw_metadata['trkn'][0][0]) - 1
            disc_num = int(raw_metadata['disk'][0][0])
        elif '----:com.apple.iTunes:MusicBrainz Album Id' in raw_metadata:
            release_id = str(raw_metadata['----:com.apple.iTunes:MusicBrainz Album Id'][0], encoding='UTF-8')
            track_num = int(raw_metadata['trkn'][0][0]) - 1
            disc_num = int(raw_metadata['disk'][0][0])
        if '----:com.apple.iTunes:KEXPPRIMARYGENRE' in raw_metadata:
            kexp_category = str(raw_metadata['----:com.apple.iTunes:KEXPPRIMARYGENRE'][0], encoding='UTF-8')
        if '----:com.apple.iTunes:KEXPFCCOBSCENITYRATING' in raw_metadata:
            kexp_obscenity_rating = str(raw_metadata['----:com.apple.iTunes:KEXPFCCOBSCENITYRATING'][0], encoding='UTF-8')


    elif _file_types[ext] == "id3":
        raw_metadata = raw_metadata.tags._DictProxy__dict
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
            
    return release_id, track_num, disc_num, kexp_obscenity_rating, kexp_category
    
    
def main():
    """
    Crawls the given directory for audio files, extracting raw metadata
    and metadata from MusicBrainz.
    For success, audio file must have a release MBID in metadata.
    """
    # dict of passed choices -> what we want for category, source, and rotation
    options = {"acq": "Recent Acquisitions", "recent acquisitions": "Recent Acquisitions", "electronic": "Electronic",
               "ele": "Electronic", "exp": "Experimental", "experimental": "Experimental", "hip": "Hip Hop",
               "hip hop": "Hip Hop", "jaz": "Jazz", "jazz": "Jazz", "liv": "Live on KEXP", "live on kexp": "Live on Kexp",
               "loc": "Local", "local": "Local", "reg": "Reggae", "reggae": "Reggae", "roc": "Rock/Pop", "rock": "Rock/Pop",
               "pop": "Rock/Pop", "rock/pop": "Rock/Pop", "roo": "Roots", "roots": "Roots",
               "rot": "Rotation", "rotation": "Rotation", "sho": "Shows Around Town", "shows around town": "Shows Around Town",
               "sou": "Soundtracks", "soundtracks": "Soundtracks", "wor": "World", "world": "World",
               "cd library": "CD Library", "melly": "Melly",
               "heavy": "Heavy", "library": "Library", "light": "Light", "medium": "Medium", "r/n": "R/N"}
               
    parser = argparse.ArgumentParser(description='Get metadata from files.')
    parser.add_argument('input_directory', help="Input audio file.")
    parser.add_argument('output_directory', help="Directory to store output files. MUST ALREADY EXIST for now.")
    parser.add_argument('-d', '--delete', default=False, const=True, nargs='?', help="Delete audio files from input_directory after processing")
    parser.add_argument('-c', '--category', type=str.casefold, choices=["recent acquisitions", "acq", "electronic", "ele", "experimental", "exp", "hip hop", "hip", "jaz", "jazz", "live on kexp", "liv", "local", "reggae", "reg", "rock", "pop", "rock/pop", "roc", "roots", "roo", "rotation", "rot", "shows around town", "sho", "soundtracks", "sou", "world", "wor"], help="Category or genre of releases being filewalked")
    parser.add_argument('-s', '--source', type=str.casefold, choices=["cd library", "melly"], help="KEXPSource value - Melly or CD Library")
    parser.add_argument('-r', '--rotation', type=str.casefold, choices=["heavy", "library", "light", "medium", "r/n"], help="Rotation workflow value")
    parser.add_argument('-g', '--generate', default=False, const=True, nargs='?')
    
    args = parser.parse_args()
        
    batch_meta = {}
    batch_meta["category"] = options[args.category] if args.category != None else ""
    batch_meta["rotation"] = options[args.rotation] if args.rotation != None else ""
    batch_meta["source"] = options[args.source] if args.source != None else ""
        
    process_directory(args.input_directory, args.output_directory, batch_meta, args.generate, DaletSerializer, args.delete)


main()
