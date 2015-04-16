__author__ = 'hidat'

from yattag import Doc
import os.path as path

def serialize(metadata, release_data, track_data, old_file):
    """
    Produces a json-formatted string of all metadata

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: The track metadata from musicbrainz
    :param old_file: The name of the original file
    :return: A json-formatted string with all metadata

         <Title>EarthEE</Title>
        <KEXPArtistCredit>THEESatisfaction feat. Shabazz Palaces, Porter Ray and Erik
            Blood</KEXPArtistCredit>
        <KEXPTrackNumber>7</KEXPTrackNumber>
        <KEXPMediumNumber>1</KEXPMediumNumber>
        <KEXPAcoustID>e491f92a-e936-41fb-9ca8-9ef80e5c5cf1</KEXPAcoustID>
        <KEXPReleaseArtistSortName>THEESatisfaction</KEXPReleaseArtistSortName>
        <KEXPFCCObscenityRating>YELLOW DOT</KEXPFCCObscenityRating>
        <KEXPArtist>918c2998-512f-4e6c-95ec-0f833c4b7e22</KEXPArtist>
        <KEXPArtist>6462c4f6-6f69-4636-a835-02eebe81c90f</KEXPArtist>
        <KEXPArtist>29776ddc-f7db-4ce6-b318-707e9cc46cba</KEXPArtist>
        <KEXPArtist>bb5edacd-c97d-42df-9174-2fa7abbf69ee</KEXPArtist>
        <KEXPTrackMBID>742531b4-743f-413d-8e0c-98820bdf4f1a</KEXPTrackMBID>
        <KEXPTotalMediums>1</KEXPTotalMediums>
        <KEXPTotalTracks>13</KEXPTotalTracks>
        <KEXPReleaseArtistDistributionRule>T</KEXPReleaseArtistDistributionRule>
        <KEXPVariousArtistReleaseTitleDistributionRule>E</KEXPVariousArtistReleaseTitleDistributionRule>
        <Key1>742531b4-743f-413d-8e0c-98820bdf4f1a</Key1>
        <ItemCode>742531b4-743f-413d-8e0c-98820bdf4f1a</ItemCode>

    """

    doc, tag, text = Doc().tagtext()

    with tag('titles'):
        with tag('title'):
            with tag('KEXPRelease'):
                text(track_data["track_id"])
            with tag('KEXPRecordingMBID'):
                text(track_data["track_id"])

    return doc.getvalue()


def to_file(metadata, release_data, track_data, old_file, output_dir):
    """
    Prints json-formatted metadata to a file

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: Track metadata from musicbrainz
    :param old_file: Original name of the audio file
    :param output_dir: The directory that file is being written to
    :return:
    """
    output_file = path.join(output_dir, track_data["track_id"] + ".xml")
    curr_file = open(output_file, "w+")

    formatted_data = serialize(metadata, release_data, track_data, old_file)

    curr_file.write(formatted_data)