__author__ = 'hidat'

from yattag import Doc, indent
import os.path as path
import unicodedata

def save_track(release_data, track_data, batch_meta, output_dir):
    """
    Create an XML file of track metadata that Dalet will be happy with

    :param release_data: Processed release metadata from MusicBrainz
    :param track_data: Processed track metadata from MusicBrainz
    :param input_meta: Batch metadata (from command line)
    :param output_dir: Output directory to write XML file to
    """
    doc, tag, text = Doc().tagtext()
    
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('titles'):
        with tag('title'):
            with tag('KEXPRelease'):
                text(release_data["release_id"])
            with tag('KEXPMediumNumber'):
                text(track_data["disc_num"].__str__())
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

            if (len(batch_meta["rotation"]) > 0):
                r_status = stringCleanup(batch_meta["rotation"])
                secondary_category = "CATEGORIES/ROTATION-STAGING/" + r_status
                with tag('secondary_category'):
                    text(secondary_category)
                
            primary_category = "/i/forgot"
            if sort_name.casefold() is "various artists":
                primary_category = primary_category + track_data['various_artist_dist_rule']
            else:
                primary_category = primary_category + track_data['artist_dist_rule']
            primary_category = primary_category + sort_name + "/what"

            with tag('primary_category'):
                text(primary_category)
            with tag('KEXPReleaseArtistDistributionRule'):
                text(track_data['artist_dist_rule'])
            with tag('KEXPVariousArtistReleaseTitleDistributionRule'):
                text(track_data['various_artist_dist_rule'])
            with tag('KEXPContentType'):
                text("music library track")
            with tag('KEXPSource'):
                text(batch_meta["source"])


    formatted_data = indent(doc.getvalue())    
    output_file = path.join(output_dir, track_data["item_code"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))

def save_release(release, input_meta, output_dir):
    """
    Create an XML file of release metadata that Dalet will be happy with
    
    :param release: Processed release metadata from MusicBrainz
    :param input_meta: Batch metadata from the command line
    :param output_dir: Output directory to write XML file to
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
    glossary_title = release['release_title']
    
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag('Titles'):
        with tag('GlossaryValue'):
            with tag('Key1'):
                text(release["item_code"])
            with tag('ItemCode'):
                text(release["item_code"])
            with tag('KEXPTitle'):
                text(release['release_title'])
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
                
            glossary_title = "{0} {1} {2} {3} ".format(glossary_title, full_name, release['date'], release['country'])
            with tag('KEXPDistributionCategory'):
                text(release['distribution_category'])
                
            catalog_num_list = []
            for label in release["labels"]:
                if 'label' in label:
                    a = label['label']
                    glossary_title = "{0} {1}".format(glossary_title, a['name'])
                    with tag('KEXPlabel'):
                        text(a['id'])
                if 'catalog-number' in label:
                    catalog_num_list.append(label['catalog-number'])
            
            
            glossary_title = "{0} {1}".format(glossary_title, " ".join(release['format']))
            for catalog_num in catalog_num_list:
                glossary_title = "{0} {1}".format(glossary_title, str(catalog_num))
                
            glossary_title = glossary_title.replace('\\', '-')
            glossary_title = glossary_title.replace('/', '-')
            glossary_title = glossary_title.replace('\"', '\'')
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
                    
            if (len(input_meta["rotation"]) > 0):
                r_status = stringCleanup(input_meta["rotation"])
                with tag('KEXPReleaseRotationStatus'):
                    text(input_meta["rotation"])
            if (len(input_meta["category"]) > 0):
                with tag('KEXPPrimaryGenre'):
                    text(input_meta["category"])
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
    Create an XML file of artist metadata that Dalet will be happy with.
    
    If the artist is a group that has multiple members, not an individual, 
    all member metadata (for artists new to this batch) will also be generated.
    
    :param artist: Processed metadata from MusicBrainz for 'main' artist
    :param artist_members: Processed artist metadata from MusicBrainz for any members of 'artist'
    :param output_dir: Output directory to write XML file to
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
                    if member["type"] == 'member of band' and "direction" in member \
                            and member["direction"] == "backward":
                        with tag('KEXPMember'):
                            text(member["artist"]["id"])

    formatted_data = indent(doc.getvalue())

    output_file = path.join(output_dir, 'a' + artist["id"] + ".xml")
    with open(output_file, "wb") as f:
        f.write(formatted_data.encode("UTF-8"))


def save_one_artist(artist, tag, text):
    """
    Save the metadata for one artist

    :param artist: Processed artist metadata from MusicBrainz
    :param tag: Yattag 'tag' 
    :param text: Yattag 'text'
    """
    # mandatory fields
    with tag('Key1'):
        text(artist["item_code"])
    with tag('ItemCode'):
        text(artist["item_code"])
    with tag('title'):
        text(artist["title"])
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
                    
def stringCleanup(text):
    clean = {'\\': '-', '/': '-', '\"': '\''}
    for character, replacement in clean.items():
        text = text.replace(character, replacement)
    return text
