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
    """
		<KEXPMBID>release-xxxx-xxxx-xxxxx-xxxxxxx</KEXPMBID>
		<KEXPReleaseGroupMBID>releasegroup MBID</KEXPReleaseGroupMBID>

		<KEXPArtist>0923598e-2b97-4527-b984-5feed94c168d</KEXPArtist><!-- multiple cardinality -->
		<KEXPReleaseArtistCredit>artist 1, artist 2, etc..</KEXPReleaseArtistCredit>
		<KEXPLabel>011d1192-6f65-45bd-85c4-0400dd45693e</KEXPLabel><!-- multiple cardinality -->

		<KEXPArea>Area</KEXPArea>
		<KEXPAreaMBID>area MBID</KEXPAreaMBID>
		<KEXPASIN>ASIN dfsdsdf</KEXPASIN>
		<KEXPReleaseBarcode>Barcode</KEXPReleaseBarcode>
		<KEXPReleaseCatalogNumber>2132</KEXPReleaseCatalogNumber> <!-- multiple cardinality -->
		<KEXPCountryCode>US</KEXPCountryCode>
		<KEXPReleasePackaging>DVD</KEXPReleasePackaging> <!-- multiple cardinality -->

		<KEXPDisambiguation>Disambiguation</KEXPDisambiguation>

		<KEXPDateReleased>1999-03-22</KEXPDateReleased> <!--	short text: No specific format required -->
		<KEXPFirstReleaseDate>1999-03-25</KEXPFirstReleaseDate> <!--	short text: No specific format required -->
		<KEXPLength>10:23</KEXPLength>

		<KEXPLink>http://link 1</KEXPLink> <!-- multiple cardinality -->

		<KEXPTag>TAG 1</KEXPTag> <!-- multiple cardinality -->
		<KEXPTag>tag 2</KEXPTag>
    """

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
            with tag('KEXPMBID'):
                text(release["release_id"])
            with tag('KEXPReleaseGroupMBID'):
                text(release["release_group_id"])
            full_name = ''    
            for artist in release["artist-credit"]:
    
                if 'artist' in artist:
                    a = artist['artist']
                    full_name = full_name + a['name']
                    with tag('KEXPArtist'):
                        text(a['id'])
                else:
                    full_name = full_name + artist
            with tag('KEXPReleaseArtistCredit'):
                text(full_name)
                
            for label in release["labels"]:
                if 'label-info' in label:
                    a = label['label-info']
                    with tag('KEXPlabel'):
                        text(a['id'])

            with tag('KEXPCountryCode'):
                text(release["country"])
            with tag('KEXPASIN'):
                text(release["asin"])
            with tag('KEXPReleaseBarcode'):
                text(release["barcode"])
            with tag('KEXPReleasePackaging'):
                text(release["packaging"])
            with tag('KEXPDisambiguation'):
                text(release["disambiguation"])
            with tag('KEXPDateReleased'):
                text(release["date"])
            with tag('KEXPFirstReleaseDate'):
                text(release["first_release_date"])
            for item in release["tags"]:
                with tag('KEXPTag'):
                    text(release["tag"]["name"])
            #with tag('KEXPLength'):
            #    text(release[""])
            #for item in release["links"]:
            #    with tag('KEXPLink'):
            #        text(release[""])

    formatted_data = indent(doc.getvalue())

    output_file = path.join(output_dir, 'r' + release["release_id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))
