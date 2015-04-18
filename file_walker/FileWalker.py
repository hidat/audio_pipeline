__author__ = 'cephalopodblue'
import os
import MetaInformer
import argparse
import mutagen
import JsonSerializer
import DaletSerializer

_file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis"}

def process_directory(source_dir, output_dir):
    cached_releases = {}
    serializer = DaletSerializer
    current_release_id = ''
    for root, dir, files in os.walk(source_dir):
        for name in files:
            name = root + "/" + name
            ext = os.path.splitext(name)[1].lower()
            if ext in _file_types:
                metadata = mutagen.File(name)
                if _file_types[ext] == "vorbis":
                    release_data = dict()
                    track_data = dict()
                    if "mbid" in metadata:
                        release_id = metadata["mbid"][0]
                        track_number = int(metadata["tracknumber"][0]) - 1
                        disc_num = int(metadata["discnumber"][0])
                    elif "musicbrainz_albumid" in metadata:
                        release_id = metadata["musicbrainz_albumid"]
                        track_number = metadata["tracknumber"]
                        disc_num =  metadata["discnumber"]

                print "Processing " + name
                try:
                    if release_id != current_release_id and current_release_id != '':
                        serializer.on_current_release_done(cached_releases[current_release_id], output_dir)
                        current_release_id = release_id

                    release, release_data, track_data = MetaInformer.find_meta_release(release_id, track_number, disc_num, cached_releases)
                    if release_id not in cached_releases:
                        cached_releases[release_id] = release

                    serializer.on_track_processed(metadata, release_data, track_data, name, output_dir)

                except UnicodeDecodeError:
                    print "    ERROR: Invalid characters!"

def main():
    """
    Crawls the given directory for audio files (currently only processes FLAC) and
    extracts raw metadata (expected to be acquired by ripping using dBpoweramp) and
    metadata from musicbrainz, json-formatted.

    Currently will only correctly process flac files (or other
    """
    parser = argparse.ArgumentParser(description='Get metadata from FLAC files.')
    parser.add_argument('input_directory', help="Input audio file.")
    parser.add_argument('output_directory', help="Directory to store output files. MUST ALREADY EXIST for now.")
    args = parser.parse_args()
    process_directory(args.input_directory, args.output_directory)


main()
