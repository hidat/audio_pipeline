__author__ = 'cephalopodblue'
import os
import MBInfo
import argparse
import mutagen
import shutil
import JsonSerializer
import DaletSerializer
import csv
import hashlib
import uuid as UUID

_file_types = {".wma": "wma", ".m4a": "aac", ".mp3": "id3", ".flac": "vorbis"}

def process_directory(source_dir, output_dir, serializer, delete_processed):
    cached_mb_releases = {}
    unique_artists = {}
    current_release_id = ''

    track_meta_dir = os.path.join(output_dir, 'track_meta')
    if not os.path.exists(track_meta_dir):
        os.makedirs(track_meta_dir)
    artist_meta_dir = os.path.join(output_dir, 'artist_meta')
    if not os.path.exists(artist_meta_dir):
        os.makedirs(artist_meta_dir)
    release_meta_dir = os.path.join(output_dir, 'release_meta')
    if not os.path.exists(release_meta_dir):
        os.makedirs(release_meta_dir)
    track_dir = os.path.join(output_dir, 'track')
    if not os.path.exists(track_dir):
        os.makedirs(track_dir)
    processed_hashes = os.path.join(output_dir, 'processed_hashes')
    if not os.path.exists(processed_hashes):
        os.makedirs(processed_hashes)

    track_success_dir = os.path.join(output_dir, 'found')
    if not os.path.exists(track_success_dir):
        os.makedirs(track_success_dir)
    print("Track Success: ", track_success_dir)

    track_fail_dir = os.path.join(output_dir, 'not_found')
    if not os.path.exists(track_fail_dir):
        os.makedirs(track_fail_dir)
    print("Track Fail: ", track_fail_dir)

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
                f = open(file_name, 'rb')
                sha1.update(f.read())
                f.close()
                hash_file = os.path.join(processed_hashes, sha1.hexdigest())

                if not os.path.exists(hash_file):
                    # Get the MusicBrainz Release ID from the file
                    raw_metadata = mutagen.File(file_name)
                    release_id = ''
                    kexp_obscenity_rating = ''
                    kexp_category = ''
                    if _file_types[ext] == "vorbis":
                        if "mbid" in raw_metadata:
                            release_id = raw_metadata["mbid"][0]
                            track_num = int(raw_metadata["tracknumber"][0]) - 1
                            disc_num = int(raw_metadata["discnumber"][0])
                        elif "musicbrainz_albumid" in raw_metadata:
                            release_id = raw_metadata["musicbrainz_albumid"][0]
                            track_num = int(raw_metadata["tracknumber"][0]) - 1
                            disc_num =  int(raw_metadata["discnumber"][0])

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
                            kexp_category = raw_metadata['----:com.apple.iTunes:KEXPPRIMARYGENRE'][0]
                        if '----:com.apple.iTunes:KEXPOBSCENITYRATING' in raw_metadata:
                            kexp_category = raw_metadata['----:com.apple.iTunes:KEXPOBSCENITYRATING'][0]


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

                    if release_id > '':
                        print("Processing " + ascii(file_name))
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
                                    serializer.save_release(release, release_meta_dir)

                            # Pull metadata from MusicBrainz
                            track_data = MBInfo.process_track(mb_release, disc_num, track_num)

                            # Add KEXP added metadata from tags
                            track_data['kexp_category'] = kexp_category
                            track_data['kexp_obscenity_rating'] = kexp_obscenity_rating

                            # Assign a unique item code so we can have multiple tracks with the same MBID
                            uuid = str(UUID.uuid4())
                            track_data["item_code"] = uuid
                            
                            # Extract artist information

                            # Save the metadata
                            serializer.save_track(raw_metadata, release, track_data, file_name, track_meta_dir)

                            # Copy files to to success directory
                            target = os.path.join(track_dir, track_data["item_code"] + ext)
                            shutil.copy(file_name, target)

                            # Make a backup of original file just in case
                            copy_to_path = os.path.join(track_success_dir, path)
                            shutil.copy(file_name, target)

                            # Add any new artist to our unique artists list
                            for artist in track_data["artist-credit"]:
                                if 'artist' in artist:
                                    a = artist['artist']
                                    artist_id = a['id']
                                    if not (artist_id in unique_artists):
                                        artist_meta = MBInfo.get_artist(artist_id)
                                        unique_artists[artist_id] = a['name']
                                        artist_members = []
                                        if "artist-relation-list" in artist_meta:
                                            for member in artist_meta["artist-relation-list"]:
                                                member_id = member["artist"]["id"]
                                                if not (member_id in unique_artists):
                                                    if member["type"] == 'member of band':
                                                        unique_artists[member_id] = member["artist"]["name"]
                                                        artist_members.append(MBInfo.get_artist(member_id))

                                        serializer.save_artist(artist_meta, artist_members, artist_meta_dir)

                        except UnicodeDecodeError:
                            print("    ERROR: Invalid characters!")
                    else:
                        print("Skipping " + ascii(file_name))
                        copy_to_path = os.path.join(track_fail_dir, path)

                    # Move the file out of the source directory
                    if copy_to_path > '':
                        if not os.path.exists(copy_to_path):
                            os.makedirs(copy_to_path)
                        target = os.path.join(copy_to_path, src_name)
                        if delete_processed:
                            shutil.move(file_name, target)
                        else:
                            shutil.copy(file_name, target)

                    hash_file_d = open(hash_file, 'w+')
                    hash_file_d.write(ascii(file_name))
                    hash_file_d.close()


def main():
    """
    Crawls the given directory for audio files (currently only processes FLAC) and
    extracts raw metadata (expected to be acquired by ripping using dBpoweramp) and
    metadata from musicbrainz, json-formatted.

    Currently will only correctly process flac files (or other
    """
    parser = argparse.ArgumentParser(description='Get metadata from files.')
    parser.add_argument('input_directory', help="Input audio file.")
    parser.add_argument('output_directory', help="Directory to store output files. MUST ALREADY EXIST for now.")
    args = parser.parse_args()
    process_directory(args.input_directory, args.output_directory, DaletSerializer, False)


main()
