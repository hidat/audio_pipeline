__author__ = 'cephalopodblue'
import os
import argparse
import mutagen
import shutil
import csv
import hashlib
import uuid as UUID
import sys
import xml.etree.ElementTree as ET
import datetime
import MBInfo
import MetaProcessor
import DaletSerializer
import musicbrainzngs.musicbrainz as musicbrainz
import unicodedata

_file_types = set([".xml"])

def process_directory(source_dir, output_dir, glossary_list_file, input_release_meta, serializer):

    glossary_ids = []
    with open(glossary_list_file, 'r') as f:
        for line in f:
            line = unicodedata.normalize('NFKD', line).encode('ascii', 'ignore').decode()
            glossary_ids.append(line.rstrip())
    glossary_ids = set(glossary_ids)
    
    path_start = len(source_dir) + 1
    
    track_meta_dir = os.path.join(output_dir, 'track_meta')
    if not os.path.exists(track_meta_dir):
        os.makedirs(track_meta_dir)
    artist_meta_dir = os.path.join(output_dir, 'artist_meta')
    if not os.path.exists(artist_meta_dir):
        os.makedirs(artist_meta_dir)
    release_meta_dir = os.path.join(output_dir, 'release_meta')
    if not os.path.exists(release_meta_dir):
        os.makedirs(release_meta_dir)

    fail_dir = os.path.join(output_dir, 'failed')
    if not os.path.exists(fail_dir):
        os.makedirs(fail_dir)
    print("Lookup Fail: ", fail_dir)

    log_dir = os.path.join(output_dir, 'session_logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    print("Logs: ", log_dir)
    
    # A bunch of counts for dumb housekeeping / sanity checks
    list_total_count = len(glossary_ids)
    list_release_count = 0
    list_artist_count = 0
    list_unknown_count = 0
    
    unknown_artists = 0
    unknown_releases = 0
    
    total_releases = 0
    total_artists = 0
    
    release_ids = set([])
    artist_ids = set([])
    
    # set up current log file
    date_time = datetime.datetime
    ts = date_time.now()
    
    unique_log_id = ts.strftime("%d-%m-%y-%H%M%S%f.txt")
    
    # create standard log file
    log_file_name = os.path.join(log_dir, "filewalker_log_" + unique_log_id)    
    # create log of failed glossary IDs
    failed_log_name = os.path.join(fail_dir, "fail_log_" + unique_log_id)
    # log of releases that need new metadata b/c they need to be associated with an artist
    artist_release_log_name = os.path.join(log_dir, "releases_from_artists_log_" + unique_log_id)
    
    # Make a 'log' that's just a copy of the glossary list
    glossary_list_log_name = os.path.join(log_dir, "glossary_list_log_" + unique_log_id)
    shutil.copy(glossary_list_file, glossary_list_log_name)
    
    # open standard log file; we'll just open fail and artist log as necessary
    log_file = open(log_file_name, 'ab')
    
    if os.path.basename(source_dir) == '':
        # probably have an extra / in the name; check back one
        source_dir = os.path.dirname(source_dir)
    if not os.path.basename(source_dir) == 'track_meta':
        # If we're not in track_meta already, move in there
        source_dir = os.path.join(source_dir, 'track_meta')
        if not os.path.exists(source_dir):
            print("No track_meta folder around here!", file=sys.stderr)

    for root, dir, files in os.walk(source_dir):
        if len(root) > path_start:
            path = root[path_start:]
        else:
            path = ''
        for src_name in files:
            file_name = os.path.join(root, src_name)
            ext = os.path.splitext(file_name)[1].lower()
            if ext in _file_types:
                # Get the MusicBrainz Release ID from the file
                
                track_xml = ET.parse(file_name).getroot()[0]
                release_id = track_xml.find('KEXPRelease').text
                artist_id = track_xml.find('KEXPArtist').text
                
                if release_id in glossary_ids:
                    # Keep track of how many glossaries were releases:
                    if release_id not in release_ids:
                        list_release_count += 1
                    
                    # Put this GUID in the release id set so we know to get release XML for items
                    release_ids.add(release_id)
                    
                    # copy this track metadata
                    target = os.path.join(track_meta_dir, src_name)
                    shutil.copy(file_name, target)
                if artist_id in glossary_ids:
                    # Keep track of how many glossaries were artists:
                    if artist_id not in artist_ids:
                        list_artist_count += 1
                
                    # Put this GUID in the artist id set so we know to get artist XML for items
                    artist_ids.add(artist_id)
                                                            
                    if release_id not in release_ids:
                        # make a note of releases re-metadataed b/c of artist in the artist_release_log
                        with open(artist_release_log_name, 'ab') as f:
                            log_text = "artist\t" + artist_id + "\trelease\t" + release_id + "\r\n"
                            f.write(log_text.encode("UTF-8"))
                        
                    # Put release ID of track associated with this artist in release id set
                    # so we get new XML for releases associated with this artist
                    release_ids.add(release_id)

                    # copy this track metadata
                    target = os.path.join(track_meta_dir, src_name)
                    shutil.copy(file_name, target)
                    
    # Completed track XML processing; get release & artist metadata

    glossary_ids = glossary_ids.difference(set(release_ids))
    glossary_ids = glossary_ids.difference(set(artist_ids))
    
    list_unknown_count = len(glossary_ids)
    
    # All glossary ids in release_ids are definitely releases, so just do a standard serialization
    # There should not be duplicates, and frankly if there are I'm not going to bother filtering them out right now.
    print("\nBEGINNING RELEASE GLOSSARY PROCESSING")
    for release_id in release_ids:
        print("Processing release " + str(release_id))
        try:
            mb_release = MBInfo.get_release(release_id)
            
            total_releases += 1
            
            release = MetaProcessor.process_release(mb_release)
            # save release meta
            serializer.save_release(release, input_release_meta, release_meta_dir)
            # save release to log
            log_file.write(release["log_text"].encode("UTF-8"))
            for label in release["labels"]:
                if 'label' in label:
                    label_log = "label\t" + str(label['label']['id']) + "\t" + str(label['label']['name']) + "\r\n"
                    log_file.write(label_log.encode("UTF-8"))
        except musicbrainz.ResponseError:
            # if somehow a non-valid release MBID got in the release_ids dict
            # move it back into the glossary_ids list to try at end:
            System.out.println("MUSICBRAINZ RESPONSE ERROR ON RELEASE " + release_id)
            glossary_ids.append(release_id)
    
    # All glossary IDs in artist_ids are definitely artists. Standard artist meta serialization.
    print("\nBEGINNING ARTIST GLOSSARY PROCESSING")
    for artist_id in artist_ids:
        try:
            print("Processing artist " + str(artist_id))
            mb_artist = MBInfo.get_artist(artist_id)
            
            total_artists += 1
            
            artist_members = []
            if "artist-relation-list" in mb_artist:
                for member in mb_artist["artist-relation-list"]:
                    member_id = member['artist']['id']
                    if member['type'] == 'member of band' and "direction" in member \
                            and member["direction"] == "backward":
                        artist_members.append(MBInfo.get_artist(member_id))
                        
            # add artist to log
            log = mb_artist['log_text']
            log_file.write(log.encode('UTF-8'))
            for member in artist_members:
                log = member['log_text']
                log_file.write(log.encode('UTF-8'))
            serializer.save_artist(mb_artist, artist_members, artist_meta_dir)
        except musicbrainz.ResponseError:
            # If somehow a nonvalid artist MBID got in the artist_ids dict
            # move it back into the glossary_ids list to try at end:
            System.out.println("MUSICBRAINZ RESPONSE ERROR ON ARTIST " + artist_id)
            glossary_ids.append(artist_id)

    # Hopefully all glossary IDs have been properly sorted, but if they haven't:
    # First try w/ glossary ID as artist ID, then w/ glossary ID as release ID
    # For release IDs, we'll just pretend that the disc number is 1 (for now)
    print("\nPROCESSING UNKNOWN GLOSSARIES")
    for glossary_id in glossary_ids:
        try:
            print("Processing " + str(glossary_id) + " as artist")
            mb_artist = MBInfo.get_artist(glossary_id)
            
            # successfully retrieved artist info, so this is an artist. increment counter.
            unknown_artists += 1
            total_artists += 1
            
            artist_members = []
            if "artist-relation-list" in mb_artist:
                for member in mb_artist["artist-relation-list"]:
                    member_id = member['artist']['id']
                    if member['type'] == 'member of band' and "direction" in member \
                            and member["direction"] == "backward":
                        artist_members.append(MBInfo.get_artist(member_id))
                        
            # add artist to log
            log = mb_artist['log_text']
            log_file.write(log.encode('UTF-8'))
            for member in artist_members:
                log = member['log_text']
                log_file.write(log.encode('UTF-8'))
            serializer.save_artist(mb_artist, artist_members, artist_meta_dir)
        except musicbrainz.ResponseError:
            try:
                # Glossary ID was not an artist ID, so we'll try again as release ID
                print("Processing " + str(glossary_id) + " as release")
                mb_release = MBInfo.get_release(glossary_id)
                
                # successfully retrieved release info, so this is a release. increment counter.
                unknown_releases += 1
                total_releases += 1
                
                release = MetaProcessor.process_release(mb_release)
                # save release meta
                serializer.save_release(release, input_release_meta, release_meta_dir)
                # save release to log
                log_file.write(release["log_text"].encode("UTF-8"))
                for label in release["labels"]:
                    if 'label' in label:
                        label_log = "label\t" + str(label['label']['id']) + "\t" + str(label['label']['name']) + "\r\n"
                        log_file.write(label_log.encode("UTF-8"))
                
            # Glossary ID was neither artist nor release ID; print error message and move ID to failed log
            except musicbrainz.ResponseError:
                print("ERROR: " + str(glossary_id) + " is not a valid artist or release MBID!")
                with open(failed_log_name, 'a') as f:
                    f.write(glossary_id)
                                        
    print("Total number of glossaries passed in: " + str(list_total_count))
    print("Number of glossaries in list that are releases: " + str(list_release_count))
    print("Number of glossaries in list that are artists: " + str(list_artist_count))
    print("Number of glossaries in list that were unknown: " + str(list_unknown_count))
    print("Number of unknown that are releases: " + str(unknown_releases))
    print("Number of unknown that are artists: " + str(unknown_artists))
    log_file.close()
       
def main():
    """
    Crawls the given directory and makes a copy of all releases with MBIDs matching the passed list
    """
    options = {"acq": "Recent Acquisitions", "recent acquisitions": "Recent Acquisitions", "electronic": "Electronic",
               "ele": "Electronic", "exp": "Experimental", "experimental": "Experimental", "hip": "Hip Hop",
               "hip hop": "Hip Hop", "jaz": "Jazz", "jazz": "Jazz", "liv": "Live on KEXP", "live on kexp": "Live on Kexp",
               "loc": "Local", "local": "Local", "reg": "Reggae", "reggae": "Reggae", "roc": "Rock/Pop", "rock": "Rock/Pop",
               "pop": "Rock/Pop", "rock/pop": "Rock/Pop", "roo": "Roots", "roots": "Roots",
               "rot": "Rotation", "rotation": "Rotation", "sho": "Shows Around Town", "shows around town": "Shows Around Town",
               "sou": "Soundtracks", "soundtracks": "Soundtracks", "wor": "World", "world": "World",
               "heavy": "Heavy", "library": "Library", "light": "Light", "medium": "Medium", "r/n": "R/N"}

    parser = argparse.ArgumentParser(description='Get metadata of a list of release & artist GUIDs, as well as all associated tracks and releases. \
                To be used with track metadata XML files that are associated with the specified release and artist GUIDs.')
    parser.add_argument('input_directory', help="Directory of previous batch.")
    parser.add_argument('output_directory', help="Output metadata directory.")
    parser.add_argument('glossary_list_file', help="File containing a list of glossary ids")
    parser.add_argument('-c', '--category', type=str.casefold, choices=["recent acquisitions", "acq", "electronc", "ele", "experimental", "exp", "hip hop", "hip", "jaz", "jazz", "live on kexp", "liv", "local", "reggae", "reg", "rock", "pop", "rock/pop", "roc", "roots", "roo", "rotation", "rot", "shows around town", "sho", "soundtracks", "sou", "world", "wor"], help="Category or genre of releases being filewalked")
    parser.add_argument('-r', '--rotation', type=str.casefold, choices=["heavy", "library", "light", "medium", "r/n"], help="Rotation workflow value")

    args = parser.parse_args()
    
    input_release_meta = {}
    input_release_meta["category"] = options[args.category] if args.category != None else ""
    input_release_meta["rotation"] = options[args.rotation] if args.rotation != None else ""

    process_directory(args.input_directory, args.output_directory, args.glossary_list_file, input_release_meta, DaletSerializer)

main()
