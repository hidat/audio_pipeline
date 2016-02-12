__author__ = 'hidat'

from yattag import Doc, indent
import os.path as path
import unicodedata
import os
import datetime

class DaletSerializer:
    def __init__(self, output_dir):
        # Set up metadata directories
        self.track_meta_dir = os.path.join(output_dir, 'track_meta')
        if not os.path.exists(self.track_meta_dir):
            os.makedirs(self.track_meta_dir)
        print("Track meta: ", self.track_meta_dir)
        
        self.artist_meta_dir = os.path.join(output_dir, 'artist_meta')
        if not os.path.exists(self.artist_meta_dir):
            os.makedirs(self.artist_meta_dir)
        print("Artist meta: ", self.artist_meta_dir)
        
        self.release_meta_dir = os.path.join(output_dir, 'release_meta')
        if not os.path.exists(self.release_meta_dir):
            os.makedirs(self.release_meta_dir)
        print("Release meta: ", self.release_meta_dir)
        
        self.log_dir = os.path.join(output_dir, 'session_logs')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        print("Logs: ", self.log_dir)
        
        # set up current log file
        date_time = datetime.datetime
        ts = date_time.now()
        # create & open log file
        self.log_file_name = os.path.join(self.log_dir, ts.strftime("filewalker_log_%d-%m-%y-%H%M%S%f.txt"))


    def save_track(self, meta_processor, disc_num, track_num):
        """
        Create an XML file of track metadata that Dalet will be happy with

        :param release_data: Processed release metadata from MusicBrainz
        :param track_data: Processed track metadata from MusicBrainz
        :param batch_meta: Batch metadata (from command line)
        :param output_dir: Output directory to write XML file to
        """
        doc, tag, text = Doc().tagtext()
        
        release_data = meta_processor.get_release()
        track_data = meta_processor.get_track(disc_num, track_num)
        output_dir = self.track_meta_dir
        
        with open(self.log_file_name, 'ab') as log_file:
            log_file.write(track_data['log'].encode('UTF-8'))
        
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

                if 'secondary_category' in track_data:
                    with tag('secondary_category'):
                        text(track_data['secondary_category'])
                    
                with tag('KEXPReleaseArtistDistributionRule'):
                    text(track_data['artist_dist_rule'])
                with tag('KEXPVariousArtistReleaseTitleDistributionRule'):
                    text(track_data['various_artist_dist_rule'])
                with tag('KEXPContentType'):
                    text("music library track")
                with tag('KEXPSource'):
                    text(meta_processor.batch_meta["source"])


        formatted_data = indent(doc.getvalue())    
        output_file = path.join(output_dir, track_data["item_code"] + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))

    def save_release(self, meta_processor):
        """
        Create an XML file of release metadata that Dalet will be happy with
        
        :param release: Processed release metadata from MusicBrainz
        :param batch_meta: Batch metadata from the command line
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

        release = meta_processor.get_release()
        output_dir = self.release_meta_dir
        batch_meta = meta_processor.batch_meta
        
        with open(self.log_file_name, 'ab') as log_file:
            log_file.write(release['log_text'].encode('UTF-8'))
            for label in release['labels']:
                if 'label' in label:
                    label_log = "label\t" + str(label['label']['id']) + "\t" + str(label['label']['name']) + "\r\n"
                    log_file.write(label_log.encode("UTF-8"))
        
        
        doc, tag, text = Doc().tagtext()
                
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
                        
                if (len(batch_meta["rotation"]) > 0):
                    r_status = stringCleanup(batch_meta["rotation"])
                    with tag('KEXPReleaseRotationStatus'):
                        text(batch_meta["rotation"])
                if (len(batch_meta["category"]) > 0):
                    with tag('KEXPPrimaryGenre'):
                        text(batch_meta["category"])
                #with tag('KEXPLength'):
                #    text(release[""])
                #for item in release["links"]:
                #    with tag('KEXPLink'):
                #        text(release[""])

        formatted_data = indent(doc.getvalue())

        
        output_file = path.join(output_dir, 'r' + release["release_id"] + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))

    def save_artist(self, artist, artist_members):
        """
        Create an XML file of artist metadata that Dalet will be happy with.
        
        If the artist is a group that has multiple members, not an individual, 
        all member metadata (for artists new to this batch) will also be generated.
        
        :param artist: Processed metadata from MusicBrainz for 'main' artist
        :param artist_members: Processed artist metadata from MusicBrainz for any members of 'artist'
        :param output_dir: Output directory to write XML file to
        """

        output_dir = self.artist_meta_dir
        with open(self.log_file_name, 'ab') as log_file:
            log = artist["log_text"]
            log_file.write(log.encode("UTF-8"))
            for member in artist_members:
                log_file.write(member["log_text"].encode("UTF-8"))
        
        doc, tag, text = Doc().tagtext()

        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('Titles'):
            for member in artist_members:
                with tag('GlossaryValue'):
                    self.save_one_artist(member, tag, text)

            with tag('GlossaryValue'):
                self.save_one_artist(artist, tag, text)

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


    def save_one_artist(self, artist, tag, text):
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
