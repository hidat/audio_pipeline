__author__ = 'cephalopodblue'
import os
import MBInfo
import argparse
import mutagen
import JsonSerializer
import DaletSerializer

_file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis"}

def process_directory(source_dir, output_dir, serializer):
    cached_mb_releases = {}
    current_release_id = ''
    for root, dir, files in os.walk(source_dir):
        for file_name in files:
            file_name = root + "/" + file_name
            ext = os.path.splitext(file_name)[1].lower()
            if ext in _file_types:

                # Get the MusicBrainz Release ID from the file
                raw_metadata = mutagen.File(file_name)
                release_id = ''
                if _file_types[ext] == "vorbis":
                    if "mbid" in raw_metadata:
                        release_id = raw_metadata["mbid"][0]
                        track_num = int(raw_metadata["tracknumber"][0]) - 1
                        disc_num = int(raw_metadata["discnumber"][0])
                    elif "musicbrainz_albumid" in raw_metadata:
                        release_id = raw_metadata["musicbrainz_albumid"]
                        track_num = raw_metadata["tracknumber"]
                        disc_num =  raw_metadata["discnumber"]

                if release_id > '':
                    print "Processing " + file_name
                    try:
                        # Check if this is a new release (generally means we are in a new directory)
                        if release_id != current_release_id:
                            current_release_id = release_id

                            #See if we have already cached the release, or we need to pull if from MusicBrainz
                            if release_id in cached_mb_releases:
                                mb_release = cached_mb_releases[release_id]
                            else:
                                mb_release = MBInfo.get_release(release_id)
                                cached_mb_releases[release_id] = mb_release
                                release = MBInfo.process_release(mb_release, disc_num)
                                serializer.save_release(release, output_dir)

                        track_data = MBInfo.process_track(mb_release, disc_num, track_num)

                        serializer.save_track(raw_metadata, release, track_data, file_name, output_dir)

                    except UnicodeDecodeError:
                        print "    ERROR: Invalid characters!"
                else:
                    print "Skipping " + file_name
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
    process_directory(args.input_directory, args.output_directory, DaletSerializer)


main()
