import argparse
import hashlib
import os
import shutil

from audio_pipeline import Constants
from audio_pipeline.util import Process as Processor
from audio_pipeline.util import AudioFileFactory
from audio_pipeline.util import Exceptions
from audio_pipeline.util import MBInfo
from audio_pipeline.util import Util


def process_directory(source_dir, output_dir):
    batch_constants = Constants.batch_constants

    # If copying audio (not just generating metadata),
    # get the locations that audio files will be copied to
    serializer = Constants.serializer(output_dir)
    track_dir, track_success_dir, track_fail_dir = '', '', ''
    if not batch_constants.meta_only:
        track_dir, track_success_dir, track_fail_dir = audio_directories(output_dir)

    # Get directories for processed hashes
    processed_hashes = info_directories(output_dir)
    
    # create a MBInfo object to get MusicBrainz metadata
    mbinfo = MBInfo.MBInfo(batch_constants.initial_server)
    # Set the (metadata) processor's mbinfo object
    processor = Processor.Processor(mbinfo, Constants.processor)
    
    af = AudioFileFactory.AudioFileFactory
    
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
                audio_file = af.get(file_name)
                
                # check if file is in processed_hash directory
                sha1 = hashlib.sha1()
                with open(file_name, 'rb') as f:
                    sha1.update(f.read())
                    
                hash_file = os.path.join(processed_hashes, sha1.hexdigest())
                
                if not os.path.exists(hash_file):
                    # Get the MusicBrainz Release ID from the file
                    if Util.has_mbid(audio_file):
                        print("Processing " + ascii(file_name))

                        try:
                            # process track's metadata:
                            if audio_file.mbid.value in processor.releases:
                                release_meta = processor.get_release(audio_file.mbid.value)
                                release = release_meta.release
                            else:
                                release_meta = processor.get_release(audio_file.mbid.value)
                                release = release_meta.release

                                # serialize the release
                                serializer.save_release(release)

                            # Serialize track metadata
                            track = release_meta.get_track(audio_file)
                            serializer.save_track(release, track)
                            
                            # Make a copy of the original file (just in case)
                            copy_to_path = os.path.join(track_success_dir, path)                            
                            
                            if batch_constants.artist_gen:
                                for artist in track.artists:
                                    # Save artist meta if we have not already.
                                    if artist not in processor.artists:
                                    
                                        artist_meta = processor.get_artist(artist)
                                        artist = artist_meta.artist
                                        
                                        group_members = []
                                        
                                        for member in artist.group_members:
                                            if member not in processor.artists:
                                                member_meta = processor.get_artist(member)
                                                group_members.append(member_meta.artist)
                                                
                                        serializer.save_artist(artist, group_members)
                                    
                            # move track to success directory (if we're copying files)
                            if not batch_constants.meta_only:
                                ext = os.path.splitext(file_name)[1].lower()
                                target = os.path.join(track_dir, track.item_code + ext)
                                shutil.copy(file_name, target)
                                
                        # Move the file out of the source directory
                        except UnicodeDecodeError:
                            print("    ERROR: Invalid characters!")
                            copy_to_path = os.path.join(track_fail_dir, path)

                    with open(hash_file, 'w+') as hash_file_d:
                        hash_file_d.write(ascii(file_name))

            except Exceptions.UnsupportedFiletypeError as e:
                # just skip unsupported filetypes??
                print("Skipping " + ascii(file_name))
                copy_to_path = os.path.join(track_fail_dir, path)
            except IOError as e:
                print("Error reading file {0}".format(ascii(file_name)))
                print("Skipping " + ascii(file_name))
                copy_to_path = os.path.join(track_fail_dir, path)

            if not batch_constants.meta_only and copy_to_path > '':
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

    config_dir = os.path.split(os.path.abspath(__file__))[0]
    Constants.load_config(config_dir)

    parser = argparse.ArgumentParser(description='Get metadata from files.')
    
    if Constants.argument_config:
        parser = Constants.argument_config(parser)

    parser.add_argument('input_directory', help="Input audio file.")
    parser.add_argument('output_directory', help="Directory to store output files.")

        
    parser.add_argument('-p', '--profile', type=str.casefold, help="Specify a user profile. If a profile with this"
                                                                   " name does not exist, it will be created.")

    parser.add_argument('-d', '--delete', metavar='', default=False, const=True, nargs='?',
                        help="Delete audio files from input_directory after processing")
    parser.add_argument('--local', help="Set local MusicBrainz server address")
    parser.add_argument('--remote', help="Set remote MusicBrainz server address")
    parser.add_argument('--mbhost', type=str.casefold,
                        help="Specify the server to retrieve MusicBrainz data from. Default is musicbrainz.org; "
                             "another server can be manually specified")
    parser.add_argument('-g', '--generate', default=False, const=True, nargs='?',
                        help="Generate metadata only; don't copy any files")
    parser.add_argument('-i', '--gen_item_code', default=False, const=True, nargs='?',
                        help="Generate a unique item code for all audio files")
    parser.add_argument('--mb_server', default="lr", type=str.casefold, metavar="\'r\': Remote only,\
                        \'l\': local only, \'lr\': local then remote, \'rl\': remote then local",
                        choices=["r", "l", "lr", "rl"],
                        help='Specify what server(s) to retrive MusicBrainz meta from.' )
    args = parser.parse_args()

    Constants.setup(args, args.profile)

    process_directory(Constants.batch_constants.input_directory, Constants.batch_constants.output_directory)

if __name__ == "__main__":
    main()
