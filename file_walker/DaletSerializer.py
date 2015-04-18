__author__ = 'hidat'

from yattag import Doc, indent
import os.path as path

def serialize(metadata, release_data, track_data, old_file):
    """
    Produces a json-formatted string of all metadata

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: The track metadata from musicbrainz
    :param old_file: The name of the original file
    :return: A json-formatted string with all metadata

        <KEXPRelease>abf86b2b-6a77-4e68-87e2-56a824f5a608</KEXPRelease>
        <KEXPMediumNumber>1</KEXPMediumNumber>
        <KEXPTotalMediums>1</KEXPTotalMediums>
        <KEXPAcoustID>e491f92a-e936-41fb-9ca8-9ef80e5c5cf1</KEXPAcoustID>
        <KEXPReleaseArtistSortName>THEESatisfaction</KEXPReleaseArtistSortName>
        <Key1>742531b4-743f-413d-8e0c-98820bdf4f1a</Key1>
        <ItemCode>742531b4-743f-413d-8e0c-98820bdf4f1a</ItemCode>
        <KEXPRecordingMBID>64876b1f-f85e-4329-a3c9-1e669b240122</KEXPRecordingMBID>
        <KEXPTrackMBID>742531b4-743f-413d-8e0c-98820bdf4f1a</KEXPTrackMBID>
        <Title>EarthEE</Title>
        <KEXPFCCObscenityRating>YELLOW DOT</KEXPFCCObscenityRating>
        <KEXPArtistCredit>THEESatisfaction feat. Shabazz Palaces, Porter Ray and Erik Blood</KEXPArtistCredit>
        <KEXPArtist>bb5edacd-c97d-42df-9174-2fa7abbf69ee</KEXPArtist>
        <KEXPTrackNumber>7</KEXPTrackNumber>
        <KEXPTotalTracks>13</KEXPTotalTracks>
        <KEXPReleaseArtistDistributionRule>T</KEXPReleaseArtistDistributionRule>
        <KEXPVariousArtistReleaseTitleDistributionRule>E</KEXPVariousArtistReleaseTitleDistributionRule>
    """

    doc, tag, text = Doc().tagtext()

    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('titles'):
        with tag('title'):
            with tag('KEXPRelease'):
                text(release_data["release_id"])
            with tag('KEXPMediumNumber'):
                text(release_data["disc_num"].__str__())
            with tag('KEXPTotalMediums'):
                text(release_data["disc_count"].__str__())
            for artist in release_data["artist-credit"]:
                if 'artist' in artist:
                    a = artist['artist']
                    with tag('KEXPReleaseArtistSortName'):
                        text(a['sort-name'])

            with tag('KEXPTrackMBID'):
                text(track_data["release_track_id"])
            with tag('ItemCode'):
                text(track_data["release_track_id"])
            with tag('Key1'):
                text(track_data["release_track_id"])
            with tag('KEXPRecordingMBID'):
                text(track_data["track_id"])
            with tag('Title'):
                text(track_data["title"])
            with tag('KEXPTrackNumber'):
                text(track_data["track_num"].__str__())
            with tag('KEXPTotalTracks'):
                text(track_data["track_count"].__str__())
            full_name = ""
            for artist in track_data["artist-credit"]:

                if 'artist' in artist:
                    a = artist['artist']
                    full_name = full_name + a['name']
                    with tag('KEXPArtist'):
                        text(a['id'])
                else:
                    full_name = full_name + artist
            with tag('KEXPArtistCredit'):
                text(full_name)
            with tag('KEXPReleaseArtistDistributionRule'):
                text('T')
            with tag('KEXPVariousArtistReleaseTitleDistributionRule'):
                text('E')


    return indent(doc.getvalue())


def save_track(metadata, release_data, track_data, old_file, output_dir):
    """
    Prints json-formatted metadata to a file

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: Track metadata from musicbrainz
    :param old_file: Original name of the audio file
    :param output_dir: The directory that file is being written to
    :return:
    """

    formatted_data = serialize(metadata, release_data, track_data, old_file)

    output_file = path.join(output_dir, track_data["track_id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))

def save_release(release, output_dir):
    doc, tag, text = Doc().tagtext()

    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('Titles'):
        with tag('GlossaryValue'):
            with tag('Key1'):
                text(release["release_id"])
            with tag('ItemCode'):
                text(release["release_id"])
            with tag('title'):
                text(release["release-title"])
            with tag('GlossaryType'):
                text('Release')


    formatted_data = indent(doc.getvalue())

    output_file = path.join(output_dir, 'r' + release["release_id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))
