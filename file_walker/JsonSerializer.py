__author__ = 'cephalopodblue'
import json
import os.path as path

def serialize(metadata, release_data, track_data, old_file):
    """
    Produces a json-formatted string of all metadata

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: The track metadata from musicbrainz
    :param old_file: The name of the original file
    :return: A json-formatted string with all metadata
    """
    assets = dict()
    assets["file"] = str(track_data["track_id"])
    assets["old_file"] = path.basename(old_file)

    raw_meta = {}
    for tag_name, tag_value in metadata.iteritems():
        try:
            json.dumps(tag_value)
        except TypeError:
            tag_value = str(tag_value)
        raw_meta[tag_name] = tag_value

    assets["raw_meta"] = raw_meta
    assets["release"] = release_data
    assets["track"] = track_data

    return json.dumps({"assets": assets})


def serialize_print(metadata, release_data, track_data, old_file, output_dir):
    """
    Prints json-formatted metadata to a file

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: Track metadata from musicbrainz
    :param old_file: Original name of the audio file
    :param output_dir: The directory that file is being written to
    :return:
    """
    output_file = path.join(output_dir, track_data["track_id"] + ".json")
    curr_file = open(output_file, "w+")

    formatted_data = serialize(metadata, release_data, track_data, old_file)

    curr_file.write(formatted_data)