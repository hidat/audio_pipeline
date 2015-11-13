__author__ = 'hidat'

from yattag import Doc, indent
import os.path as path

def serialize(metadata, release_data, track_data, source, old_file):
    """
    Produces a Dalet-happy XML-formatted string of all metadata

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: The track metadata from musicbrainz
    :param old_file: The name of the original file
    :return: An XML-formatted string with all metadata

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
        <KEXPContentType>music library track</KEXPContentType>
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
            # keep track of artist sort-name for KEXPReleaseArtistDistributionRule
            sort_name = " "
            for artist in release_data["artist-credit"]:
                if 'artist' in artist:
                    a = artist['artist']
                    with tag('KEXPReleaseArtistSortName'):
                        sort_name = a['sort-name']
                        text(sort_name)
            with tag('KEXPTrackMBID'):
                text(track_data["release_track_id"])
            with tag('ItemCode'):
                text(track_data["item_code"])
            with tag('Key1'):
                text(track_data["item_code"])
            with tag('KEXPRecordingMBID'):
                text(track_data["track_id"])
            with tag('Title'):
                text(track_data["title"])
            with tag('KEXPTrackNumber'):
                text(track_data["track_num"].__str__())
            with tag('KEXPTotalTracks'):
                text(track_data["track_count"].__str__())
            with tag('KEXPPrimaryGenre'):
                text(track_data["kexp_category"].__str__())
            with tag('KEXPFCCObscenityRating'):
                text(track_data["kexp_obscenity_rating"].__str__())

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
                text(sort_name[:1])
            with tag('KEXPVariousArtistReleaseTitleDistributionRule'):
                text(release_data["release-title"][:1])
            with tag('KEXPContentType'):
                text("music library track")
            with tag('KEXPSource'):
                text(source)


    return indent(doc.getvalue())


def save_track(metadata, release_data, track_data, source, old_file, output_dir):
    """
    Prints json-formatted metadata to a file

    :param metadata: The raw metadata
    :param release_data: The release metadata from musicbrainz
    :param track_data: Track metadata from musicbrainz
    :param old_file: Original name of the audio file
    :param output_dir: The directory that file is being written to
    :return:
    """

    formatted_data = serialize(metadata, release_data, track_data, source, old_file)
    
    output_file = path.join(output_dir, track_data["item_code"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))

def save_release(release, category, output_dir):
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
            
    # glossary_title = release['release_title'] + release['artist-credit'] + release['date'] + release['country'] + release['labels'] + release['format'] + release['catalog-number']
    glossary_title = release['release-title']
    
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('Titles'):
        with tag('GlossaryValue'):
            with tag('Key1'):
                text(release["release_id"])
            with tag('ItemCode'):
                text(release["release_id"])
            with tag('KEXPTitle'):
                text(release['release-title'])
            with tag('GlossaryType'):
                text('Release')
            with tag('KEXPMBID'):
                text(release["release_id"])
            with tag('KEXPReleaseGroupMBID'):
                text(release["release_group_id"])
            full_name = ''    
            dist_cat = ''
            for artist in release["artist-credit"]:
    
                if 'artist' in artist:
                    a = artist['artist']
                    full_name = full_name + a['name']
                    with tag('KEXPArtist'):
                        text(a['id'])

                    dist_cat = a['sort-name']
                    if 'disambiguation' in a:
                        dist_cat = dist_cat + ' (' + a['disambiguation'] + ')'
                else:
                    full_name = full_name + artist
                    dist_cat = full_name
            with tag('KEXPReleaseArtistCredit'):
                text(full_name)
                
            glossary_title = glossary_title + " " + full_name + " " + release['date'] + " " + release['country']
                
            with tag('KEXPDistributionCategory'):
                text(dist_cat)
                
            catalog_num_list = []
            for label in release["labels"]:
                if 'label-info' in label:
                    a = label['label-info']
                    glossary_title = glossary_title + " " + a['id']
                    catalog_num_list.append(a['catalog-number'])
                    with tag('KEXPlabel'):
                        text(a['id'])

            glossary_title = glossary_title + " " + release['format']
            for catalog_num in catalog_num_list:
                glossary_title = glossary_title + " " + str(catalog_num)
            with tag('title'):
                text(glossary_title)
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
            if "first_release_date" in release:
              with tag('KEXPFirstReleaseDate'):
                  text(release["first_release_date"])
            for item in release["tags"]:
                with tag('KEXPTag'):
                    text(release["tag"]["name"])
            with tag('KEXPCategory'):
                text(category)
            #with tag('KEXPLength'):
            #    text(release[""])
            #for item in release["links"]:
            #    with tag('KEXPLink'):
            #        text(release[""])

    formatted_data = indent(doc.getvalue())

    output_file = path.join(output_dir, 'r' + release["release_id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))

def save_artist(artist, artist_members, output_dir):
    """

    :param artist:
    :param output_dir:
    :return:
    """

    doc, tag, text = Doc().tagtext()

    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('Titles'):
        for member in artist_members:
            with tag('GlossaryValue'):
                save_one_artist(member, tag, text)

        with tag('GlossaryValue'):
            save_one_artist(artist, tag, text)

            if "artist-relation-list" in artist:
                for member in artist["artist-relation-list"]:
                    if member["type"] == 'member of band':
                        with tag('KEXPMember'):
                            text(member["artist"]["id"])

    formatted_data = indent(doc.getvalue())

    output_file = path.join(output_dir, 'r' + artist["id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))


def save_one_artist(artist, tag, text):
    """
    Save one artist data

    :param artist:
    :param tag:
    :param text:
    :return:
    """
    # mandatory fields
    with tag('Key1'):
        text(artist["id"])
    with tag('ItemCode'):
        text(artist["id"])
    title = artist["name"]
    if "disambiguation" in artist:
        title = title + " (" + artist["disambiguation"] + ")"
    with tag('title'):
        text(title)
    with tag('GlossaryType'):
        text('Artist')
    with tag('KEXPName'):
        text(artist["name"])
    with tag('KEXPSortName'):
        text(artist["sort-name"])
    with tag('KEXPMBID'):
        text(artist["id"])

    # optional fields

    if "alias-list" in artist:
        for alias in artist["alias-list"]:
            if 'alias' in alias:
                with tag('KEXPAlias'):
                    text(alias['alias'])

    if "annotation" in artist:
        if "annotation" in artist["annotation"]:
            with tag('KEXPAnnotation'):
                text(artist["annotation"]["text"])

    if "disambiguation" in artist:
        with tag('KEXPDisambiguation'):
            text(artist["disambiguation"])

    if "type" in artist:
        with tag('KEXPArtistType'):
            text(artist["type"])
    if "begin-area" in artist:
        with tag('KEXPBeginArea'):
            text(artist["begin-area"]["name"])
        with tag('KEXPBeginAreaMBID'):
            text(artist["begin-area"]["id"])

    if "life-span" in artist:
        if "begin" in artist["life-span"]:
            with tag('KEXPBeginDate'):
                text(artist["life-span"]["begin"])
        if "end" in artist["life-span"]:
            with tag('KEXPEndDate'):
                text(artist["life-span"]["end"])
            if 'ended' in artist["life-span"]:
                if artist["life-span"]["ended"].lower() == "true":
                    with tag('KEXPEnded'):
                        text("1")
                else:
                    with tag('KEXPEnded'):
                        text("0")

    if "country" in artist:
        with tag('KEXPCountry'):
            text(artist["area"]["name"])
        with tag('KEXPCountryMBID'):
            text(artist["area"]["id"])
    if "end-area" in artist:
        with tag('KEXPEndArea'):
            text(artist["end-area"]["name"])
        with tag('KEXPEndAreaMBID'):
            text(artist["end-area"]["id"])

    if "ipi-list" in artist:
        for code in artist["ipi-list"]:
            with tag('KEXPIPICode'):
                text(code)

    if "isni-list" in artist:
        for code in artist["isni-list"]:
            with tag('KEXPISNICode'):
                text(code)

    if "url-relation-list" in artist:
        for link in artist["url-relation-list"]:
            if 'target' in link:
                with tag('KEXPLink'):
                    text(link['target'])