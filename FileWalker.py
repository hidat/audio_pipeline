import os
import Settings
from util import MBInfo
from util import AudioFile
from file_walker import Process as Processor
from file_walker.Resources import BatchConstants as batch_constants
import serializers
import argparse
import mutagen
import shutil
import csv
import hashlib
import uuid as UUID
import sys
import datetime


def process_directory(source_dir, output_dir, serializer):
    cached_mb_releases = {}
    unique_artists = {}
    unique_labels = set([])
    current_release_id = ''
    
    # If copying audio (not just generating metadata), 
    # get the locations that audio files will be copied to
    track_dir, track_success_dir, track_fail_dir = '', '', ''
    if not batch_constants.generate:
        track_dir, track_success_dir, track_fail_dir = audio_directories(output_dir)

    # Get directories for processed hashes
    processed_hashes = info_directories(output_dir)
    
    # create a MBInfo object to get MusicBrainz metadata
    mbinfo = MBInfo.MBInfo(batch_constants.mbhost)
    # Set the (metadata) processor's mbinfo object
    Processor.Processor.mb = mbinfo
    
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
            
            try:
                audio_file = AudioFile.AudioFile(file_name)
                
                # check if file is in processed_hash directory
                sha1 = hashlib.sha1()
                with open(file_name, 'rb') as f:
                    sha1.update(f.read())
                    
                hash_file = os.path.join(processed_hashes, sha1.hexdigest())
                
                if not os.path.exists(hash_file):
                    # Get the MusicBrainz Release ID from the file
                    if audio_file.mbid.value > '':
                        print("Processing " + ascii(file_name))

                        try:
                            # process track's metadata:
                            if audio_file.mbid.value in Processor.ReleaseProcessor.releases:
                                release_meta = Processor.ReleaseProcessor.releases[audio_file.mbid.value]
                                release = release_meta.get_release()
                            else:
                                release_meta = Processor.ReleaseProcessor(audio_file.mbid.value)
                                release = release_meta.get_release()

                                # serialize the release
                                serializer.save_release(release)
                                
                            
                            # Serialize track metadata
                            track = release_meta.get_track(audio_file)
                            serializer.save_track(release, track)
                            
                            # Make a copy of the original file (just in case)
                            copy_to_path = os.path.join(track_success_dir, path)                            
                            
                            for artist in track.artists:
                                # Save artist meta if we have not already.
                                if artist not in Processor.ArtistProcessor.artists:
                                
                                    artist_meta = Processor.ArtistProcessor(artist)
                                    artist = artist_meta.get_artist()
                                    
                                    group_members = []
                                    
                                    for member in artist.group_members:
                                        if member not in Processor.ArtistProcessor.artists:
                                            member_meta = Processor.ArtistProcessor(member)
                                            group_members.append(member_meta.get_artist())
                                            
                                    serializer.save_artist(artist, group_members)
                                    
                            # move track to success directory (if we're copying files)
                            if not batch_constants.generate:
                                ext = os.path.splitext(file_name)[1].lower()
                                target = os.path.join(track_dir, track.item_code + ext)
                                shutil.copy(file_name, target)
                                
                        # Move the file out of the source directory
                        except UnicodeDecodeError:
                            print("    ERROR: Invalid characters!")
                            copy_to_path = os.path.join(track_fail_dir, path)

                
                    with open(hash_file, 'w+') as hash_file_d:
                        hash_file_d.write(ascii(file_name))

            except AudioFile.UnsupportedFiletypeError as e:
                # just skip unsupported filetypes??
                print("Skipping " + ascii(file_name))
                copy_to_path = os.path.join(track_fail_dir, path)
            except IOError as e:
                print("Error reading file {0}".format(ascii(file_name)))
                print("Skipping " + ascii(file_name))
                copy_to_path = os.path.join(track_fail_dir, path)

            if not batch_constants.generate:
                # If we aren't just generating metadata, make backup of original file just in case
                if not os.path.exists(copy_to_path):
                    os.makedirs(copy_to_path)
                    
                target = os.path.join(copy_to_path, src_name)
                if batch_constants.delete:
                    shutil.move(file_name, target)
                else:
                    shutil.copy(file_name, target)
                        
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
    """
    Get the location of directories that record 'extra' information
    (currently only audio hashes)
    """
    processed_hashes = os.path.join(output_dir, 'processed_hashes')
    if not os.path.exists(processed_hashes):
        os.makedirs(processed_hashes)
        
    return processed_hashes

        
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
               "cd library": "CD Library", "melly": "Melly", "hitters": "Hitters",
               "heavy": "Heavy", "library": "Library", "light": "Light", "medium": "Medium", "r/n": "R/N"}
               
    parser = argparse.ArgumentParser(description='Get metadata from files.')
    parser.add_argument('input_directory', help="Input audio file.")
    parser.add_argument('output_directory', help="Directory to store output files. MUST ALREADY EXIST for now.")
    parser.add_argument('-d', '--delete', default=False, const=True, nargs='?', help="Delete audio files from input_directory after processing")
    parser.add_argument('-c', '--category', type=str.casefold, choices=["recent acquisitions", "acq", "electronic", "ele", "experimental", "exp", "hip hop", "hip", "jaz", "jazz", "live on kexp", "liv", "local", "reggae", "reg", "rock", "pop", "rock/pop", "roc", "roots", "roo", "rotation", "rot", "shows around town", "sho", "soundtracks", "sou", "world", "wor"], help="Category or genre of releases being filewalked")
    parser.add_argument('-s', '--source', type=str.casefold, choices=["cd library", "melly", "hitters"], help="KEXPSource value - Melly or CD Library")
    parser.add_argument('-r', '--rotation', type=str.casefold, choices=["heavy", "library", "light", "medium", "r/n"], help="Rotation workflow value")
    parser.add_argument('-l', '--local', type=str.casefold, default='musicbrainz.org', const=Settings.Settings.local_server,
                        help="Switch server to retrieve MusicBrainz metadata. Options are \'musicbrainz.org\' (default) and " + Settings.Settings.local_server + " (with flag)",
                        nargs='?')
    parser.add_argument('--mbhost', type=str.casefold,
                        help="Specify the server to retrieve MusicBrainz data from. Default is musicbrainz.org; default --server option is http://musicbrainz.kexp.org:5000/; another server can be manually specified")
    parser.add_argument('-g', '--generate', default=False, const=True, nargs='?')
    parser.add_argument('-i', '--gen_item_code', default=False, const=True, nargs='?', help="Generate a unique item code for all audio files")
    
    args = parser.parse_args()
        
    server = args.mbhost if args.mbhost != None else args.local
        
    batch_constants.category = options[args.category] if args.category != None else ""
    batch_constants.rotation = options[args.rotation] if args.rotation != None else ""
    batch_constants.source = options[args.source] if args.source != None else ""
    
    batch_constants.gen_item_code = args.gen_item_code
    batch_constants.generate = args.generate
    batch_constants.delete = args.delete
    batch_constants.local_server = args.local
    batch_constants.mbhost = args.mbhost
    
    batch_constants.input_directory = args.input_directory
    batch_constants.output_directory = args.output_directory
    
    if args.mbhost:
        batch_constants.mbhost = args.mbhost
    else:
        batch_constants.mbhost = args.local
    
    # Create the serializer (rigt now... we're just making a DaletSerializer)
    serializer = serializers.DaletSerializer.DaletSerializer(batch_constants.output_directory)
        
    process_directory(args.input_directory, args.output_directory, serializer)

if __name__ == "__main__":
    main()
